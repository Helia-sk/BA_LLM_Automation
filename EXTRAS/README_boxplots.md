# Model Performance Box Plot Generator

This program creates comprehensive box plots for analyzing model performance data deviation across multiple runs.

## Features

- **Box Plots**: Visualize accuracy distribution for each model
- **Violin Plots**: Show detailed distribution shapes
- **Statistical Analysis**: Calculate mean, standard deviation, range, and coefficient of variation
- **Run Comparison**: Compare performance across different runs
- **Detailed Tables**: Comprehensive performance comparison tables

## Generated Visualizations

1. **model_performance_boxplots.png**: Main analysis with 4 subplots:
   - Box plot by model
   - Violin plot for distribution shape
   - Box plot with run numbers
   - Statistical summary table

2. **detailed_model_analysis.png**: Detailed analysis with:
   - Bar chart with error bars
   - Individual data points
   - Comprehensive comparison table

## Usage

### Quick Start
```bash
# Windows
run_boxplots.bat

# Cross-platform
python run_boxplots.py
```

### Direct Usage
```bash
# Install requirements
pip install -r requirements_boxplots.txt

# Run analysis
python model_performance_boxplots.py
```

## Data Format

The program expects data in the following format:
```
MODEL_NAME	29	26	3	0	89.66%	10.34%
```

Where:
- First column: Model name
- Last few columns: Accuracy percentages

## Analysis Results

The program analyzes the following models from your data:

1. **CO_CSV_ANCHORED_gpt-4o-mini_prompt18**: 90.81% ± 1.99% (CV: 2.19%)
2. **CO_CSV_ANCHORED_gpt-4o_prompt18**: 36.78% ± 1.99% (CV: 5.42%)
3. **CO_CSV_ANCHORED_deepseek-r1-14b_Prompt17**: 57.47% ± 13.05% (CV: 22.71%)
4. **CO_CSV_ANCHORED_mistral-7b_Prompt17**: 36.78% ± 10.54% (CV: 28.64%)

## Key Insights

- **Most Consistent**: gpt-4o-mini shows the lowest coefficient of variation (2.19%)
- **Most Variable**: mistral-7b shows the highest coefficient of variation (28.64%)
- **Best Performance**: gpt-4o-mini achieves the highest accuracy (90.81%)
- **Most Stable**: gpt-4o-mini has the smallest standard deviation (1.99%)

## Requirements

- Python 3.7+
- pandas
- matplotlib
- seaborn
- numpy

## Files

- `model_performance_boxplots.py`: Main analysis program
- `run_boxplots.py`: Cross-platform runner script
- `run_boxplots.bat`: Windows batch file
- `requirements_boxplots.txt`: Python dependencies
- `README_boxplots.md`: This documentation







