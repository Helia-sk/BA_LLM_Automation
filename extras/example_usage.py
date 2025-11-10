#!/usr/bin/env python3
"""
Example usage of the File LLM Automation Tool
This script demonstrates how to use the automation tool programmatically.
"""

import json
from file_llm_automation import FileProcessor, get_default_config

def example_basic_usage():
    """Example: Basic file processing"""
    print("=== Basic Usage Example ===")
    
    # Create a custom configuration
    config = get_default_config()
    config.update({
        "file_extensions": [".txt", ".md"],
        "output_directory": "./example_output",
        "model": "gpt-3.5-turbo",
        "openai_api_key": "your-api-key-here",  # Replace with actual key
        "max_tokens": 1000,
        "temperature": 0.5
    })
    
    # Create processor
    processor = FileProcessor(config)
    
    # Process files
    directory = "./sample_files"  # Replace with your directory
    prompt = "Summarize the main points of this document in 3 bullet points"
    
    print(f"Processing files in: {directory}")
    print(f"Prompt: {prompt}")
    
    # Uncomment the line below to actually run (after setting up API key)
    # results = processor.process_files(directory, prompt)
    # print(f"Results: {results}")

def example_custom_naming():
    """Example: Custom output file naming"""
    print("\n=== Custom Naming Example ===")
    
    config = get_default_config()
    config.update({
        "naming_pattern": "{original_name}_reviewed_{timestamp}",
        "output_directory": "./reviews",
        "model": "gpt-4"
    })
    
    print("This would create files like: document_reviewed_20231201_143022.txt")

def example_different_models():
    """Example: Using different models for different tasks"""
    print("\n=== Different Models Example ===")
    
    models_and_tasks = [
        ("gpt-3.5-turbo", "Summarize this content"),
        ("gpt-4", "Provide detailed analysis and suggestions"),
        ("claude-3-sonnet-20240229", "Review and improve this text")
    ]
    
    for model, task in models_and_tasks:
        print(f"Model: {model} - Task: {task}")

def create_sample_files():
    """Create some sample files for testing"""
    import os
    from pathlib import Path
    
    sample_dir = Path("./sample_files")
    sample_dir.mkdir(exist_ok=True)
    
    sample_files = {
        "document1.txt": "This is a sample document about artificial intelligence. It covers machine learning, deep learning, and neural networks. The document discusses various applications and future prospects.",
        "document2.txt": "A brief overview of Python programming. Python is a versatile language used for web development, data science, and automation. It's known for its simple syntax and powerful libraries.",
        "notes.md": "# Meeting Notes\n\n## Topics Discussed\n- Project timeline\n- Budget considerations\n- Team assignments\n\n## Action Items\n- Complete design mockups\n- Review requirements document"
    }
    
    for filename, content in sample_files.items():
        file_path = sample_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f"Created sample files in: {sample_dir}")

if __name__ == "__main__":
    print("File LLM Automation Tool - Examples")
    print("=" * 40)
    
    # Create sample files for demonstration
    create_sample_files()
    
    # Show examples
    example_basic_usage()
    example_custom_naming()
    example_different_models()
    
    print("\n" + "=" * 40)
    print("To run the actual automation:")
    print("1. Edit config.json with your API keys")
    print("2. Run: python file_llm_automation.py -d ./sample_files -p 'Your prompt here'")
    print("3. Or use: run_automation.bat for interactive mode")
