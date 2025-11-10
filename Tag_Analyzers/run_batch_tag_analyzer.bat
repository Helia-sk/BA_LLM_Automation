@echo off
echo Starting Batch Tag Analyzer...
echo.
cd /d "%~dp0"
python batch_tag_analyzer.py
echo.
echo Batch Tag Analysis Complete!
pause
