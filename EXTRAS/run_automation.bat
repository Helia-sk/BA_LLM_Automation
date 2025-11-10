@echo off
echo File LLM Automation Tool
echo ========================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check if requirements are installed
python -c "import openai, anthropic" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install requirements
        pause
        exit /b 1
    )
)

REM Check if config exists
if not exist "config.json" (
    echo Creating sample configuration...
    python file_llm_automation.py --create-config
    echo.
    echo Please edit config.json with your API keys and preferences
    echo Then run this script again
    pause
    exit /b 0
)

echo Enter the directory path containing files to process:
set /p DIRECTORY=

echo Enter your processing prompt:
set /p PROMPT=

echo.
echo Starting automation...
echo Directory: %DIRECTORY%
echo Prompt: %PROMPT%
echo.

python file_llm_automation.py --directory "%DIRECTORY%" --prompt "%PROMPT%"

echo.
echo Processing complete! Check the output directory for results.
pause
