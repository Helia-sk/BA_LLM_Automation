#!/usr/bin/env python3
"""
Test script to verify settings format
"""

def test_settings():
    """Test reading settings from settings.txt"""
    settings = {}
    try:
        with open("settings.txt", 'r', encoding='utf-8') as f:
            lines = [ln.rstrip('\n') for ln in f]

        i = 0
        while i < len(lines):
            raw = lines[i]
            line = raw.strip()
            i += 1
            if not line or line.startswith('#'):
                continue

            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()

                if key in ['API_PROMPT', 'PROMPT']:
                    prompt_lines = [value]
                    # Collect continuation lines until we hit a line that starts with a key=value pattern
                    while i < len(lines):
                        next_line = lines[i]
                        # Check if this line looks like a new setting (KEY=VALUE at start of line)
                        stripped = next_line.strip()
                        if stripped and '=' in stripped and not stripped.startswith(' ') and not stripped.startswith('\t') and not stripped.startswith('-') and not stripped.startswith('*'):
                            # This looks like a new key=value setting, stop collecting
                            break
                        else:
                            # This is part of the prompt, add it
                            prompt_lines.append(next_line)
                            i += 1
                    settings['PROMPT'] = '\n'.join(prompt_lines).strip()
                else:
                    settings[key] = value

        return settings
    except FileNotFoundError:
        print("Error: settings.txt not found!")
        return None
    except Exception as e:
        print(f"Error reading settings.txt: {str(e)}")
        return None

def main():
    print("Testing API LLM Settings Format")
    print("=" * 40)
    
    settings = test_settings()
    if settings:
        print("[OK] Settings loaded successfully!")
        print(f"Input Folders: {settings.get('INPUT_FOLDERS', 'Not found')}")
        print(f"Output Base Folder: {settings.get('OUTPUT_BASE_FOLDER', 'Not found')}")
        print(f"Model: {settings.get('MODEL', 'Not found')}")
        print(f"Runs per combination: {settings.get('RUNS_PER_COMBINATION', 'Not found')}")
        print(f"Prompt ID: {settings.get('PROMPT_IDENTIFIER', 'Not found')}")
        print(f"API Key Type: {settings.get('API_KEY_TYPE', 'Not found')}")
        print(f"Prompt length: {len(settings.get('PROMPT', ''))} characters")
        print(f"Prompt preview: {settings.get('PROMPT', '')[:100]}...")
    else:
        print("[ERROR] Failed to load settings")

if __name__ == "__main__":
    main()
