@echo off
echo Installing required packages...
pip install -r requirements_boxplots.txt

echo.
echo Running Model Performance Box Plot Generator...
python model_performance_boxplots.py

echo.
echo Analysis complete! Check the generated PNG files.
pause







