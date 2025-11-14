<<<<<<< HEAD
# File LLM Automation Tool

A powerful Python tool that automatically processes files through Large Language Models (LLMs) and saves the results. Perfect for batch processing documents, code files, or any text-based content.

## Features

- **Multi-LLM Support**: Works with OpenAI GPT models and Anthropic Claude models
- **Flexible File Processing**: Process any file type with configurable extensions
- **Smart File Reading**: Handles different text encodings automatically
- **Customizable Output**: Multiple naming patterns for output files
- **Rate Limiting**: Built-in delays to avoid API rate limits
- **Progress Tracking**: Real-time progress updates and error reporting
- **Configuration Management**: JSON-based configuration for easy customization

## Installation

1. Clone or download this repository
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

1. **Create a configuration file**:
   ```bash
   python file_llm_automation.py --create-config
   ```

2. **Edit `config.json`** with your API keys and preferences:
   ```json
   {
     "file_extensions": [".txt", ".py", ".js", ".md"],
     "output_directory": "./output",
     "naming_pattern": "original_name",
     "model": "gpt-3.5-turbo",
     "openai_api_key": "your-actual-api-key-here"
   }
   ```

3. **Run the automation**:
   ```bash
   python file_llm_automation.py --directory "path/to/your/files" --prompt "Your processing prompt here"
   ```

## Usage Examples

### Basic Usage
```bash
python file_llm_automation.py -d "C:\Documents\MyFiles" -p "Summarize this content in 3 bullet points"
```

### With Custom Config
```bash
python file_llm_automation.py -d "C:\Code\Project" -p "Review this code and suggest improvements" -c "my_config.json"
```

### Process Specific File Types
Edit `config.json` to include only the file types you want:
```json
{
  "file_extensions": [".py", ".js", ".ts"],
  "model": "gpt-4",
  "output_directory": "./code_reviews"
}
```

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `file_extensions` | List of file extensions to process | `[".txt", ".py", ".js", ".md"]` |
| `output_directory` | Directory to save processed results | `"./output"` |
| `naming_pattern` | How to name output files | `"original_name"` |
| `model` | LLM model to use | `"gpt-3.5-turbo"` |
| `max_tokens` | Maximum tokens for LLM response | `2000` |
| `temperature` | LLM creativity level (0-1) | `0.7` |
| `delay_between_files` | Seconds to wait between files | `1` |
| `openai_api_key` | Your OpenAI API key | `""` |
| `anthropic_api_key` | Your Anthropic API key | `""` |

## Naming Patterns

- `"original_name"`: `filename_processed.txt`
- `"timestamp"`: `processed_20231201_143022_filename.txt`
- `"sequential"`: `processed_0001_filename.txt`
- Custom: Use placeholders like `"{original_name}_{timestamp}"`

## Supported Models

### OpenAI Models
- `gpt-3.5-turbo`
- `gpt-4`
- `gpt-4-turbo`

### Anthropic Models
- `claude-3-sonnet-20240229`
- `claude-3-opus-20240229`
- `claude-3-haiku-20240307`

## Output Format

Each processed file generates a text file containing:
- Original file path
- Processing timestamp
- Model used
- LLM response

## Error Handling

The tool includes comprehensive error handling for:
- File reading errors (encoding issues)
- API rate limits
- Network connectivity
- Invalid file paths
- LLM processing errors

## Tips for Best Results

1. **Start Small**: Test with a few files first
2. **Use Appropriate Models**: GPT-4 for complex tasks, GPT-3.5-turbo for simple ones
3. **Adjust Temperature**: Lower (0.1-0.3) for factual tasks, higher (0.7-0.9) for creative tasks
4. **Set Delays**: Increase `delay_between_files` if you hit rate limits
5. **Monitor Output**: Check the processing summary for any errors

## Troubleshooting

### Common Issues

1. **"No API keys configured"**
   - Edit `config.json` and add your API keys

2. **"Rate limit exceeded"**
   - Increase `delay_between_files` in config
   - Check your API usage limits

3. **"File encoding error"**
   - The tool tries multiple encodings automatically
   - Check if the file is actually a text file

4. **"Model not supported"**
   - Ensure you have the correct API key for the model
   - Check model name spelling

## License

This tool is provided as-is for educational and automation purposes. Please respect API terms of service and rate limits.
=======
# BA_LLM_Automation
This repository provides a comprehensive toolkit for analyzing web session logs using Large Language Models (LLMs) to detect user conversions and drop-offs. 
>>>>>>> d7e7333d6eef73b317baea27670a8a717659de8d
