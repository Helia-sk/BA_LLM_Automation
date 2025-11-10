#!/usr/bin/env python3
"""
Model Performance Box Plot Generator

This program creates box plots for model performance data deviation analysis.
It processes model accuracy data and generates comprehensive visualizations.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import defaultdict
import re

class ModelPerformanceAnalyzer:
    def __init__(self):
        self.data = []
        self.model_stats = defaultdict(list)
        
    def parse_model_data(self, data_text):
        """Parse the raw model data text into structured format"""
        lines = data_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Split by whitespace and extract components
            parts = line.split()
            if len(parts) < 6:
                continue
                
            # Extract model name (first part)
            model_name = parts[0]
            
            # Extract accuracy percentage - look for the first percentage value
            accuracy_pct = None
            for part in parts:
                if '%' in part and not part.startswith('0.00%'):
                    try:
                        accuracy_pct = float(part.replace('%', ''))
                        break
                    except ValueError:
                        continue
            
            if accuracy_pct is not None:
                # Clean model name to extract base model
                base_model = self.extract_base_model(model_name)
                self.data.append({
                    'full_name': model_name,
                    'base_model': base_model,
                    'accuracy': accuracy_pct,
                    'run': self.extract_run_number(model_name)
                })
                self.model_stats[base_model].append(accuracy_pct)
    
    def extract_base_model(self, model_name):
        """Extract base model name from full model identifier"""
        # Remove run numbers and extract base model
        base = re.sub(r'_run\d+$', '', model_name)
        base = re.sub(r'_\d+\([^)]*\)$', '', base)
        base = re.sub(r'_\d+$', '', base)
        return base
    
    def extract_run_number(self, model_name):
        """Extract run number from model name"""
        run_match = re.search(r'run(\d+)', model_name)
        if run_match:
            return int(run_match.group(1))
        return 1
    
    def create_box_plots(self, save_path='model_performance_boxplots.png'):
        """Create comprehensive box plots for model performance"""
        if not self.data:
            print("No data to plot!")
            return
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Model Performance Analysis - Box Plots', fontsize=16, fontweight='bold')
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(self.data)
        
        # 1. Box plot by base model
        ax1 = axes[0, 0]
        base_models = list(self.model_stats.keys())
        accuracy_data = [self.model_stats[model] for model in base_models]
        
        box_plot1 = ax1.boxplot(accuracy_data, tick_labels=base_models, patch_artist=True)
        ax1.set_title('Accuracy Distribution by Model', fontweight='bold')
        ax1.set_ylabel('Accuracy (%)')
        ax1.tick_params(axis='x', rotation=45)
        
        # Color the boxes
        colors = plt.cm.Set3(np.linspace(0, 1, len(base_models)))
        for patch, color in zip(box_plot1['boxes'], colors):
            patch.set_facecolor(color)
        
        # 2. Violin plot for better distribution visualization
        ax2 = axes[0, 1]
        sns.violinplot(data=df, x='base_model', y='accuracy', ax=ax2)
        ax2.set_title('Accuracy Distribution (Violin Plot)', fontweight='bold')
        ax2.set_ylabel('Accuracy (%)')
        ax2.tick_params(axis='x', rotation=45)
        
        # 3. Box plot with run numbers
        ax3 = axes[1, 0]
        sns.boxplot(data=df, x='base_model', y='accuracy', hue='run', ax=ax3)
        ax3.set_title('Accuracy by Model and Run', fontweight='bold')
        ax3.set_ylabel('Accuracy (%)')
        ax3.tick_params(axis='x', rotation=45)
        ax3.legend(title='Run', bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 4. Statistical summary
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        # Calculate statistics
        stats_text = "Statistical Summary:\n\n"
        for model in base_models:
            accuracies = self.model_stats[model]
            mean_acc = np.mean(accuracies)
            std_acc = np.std(accuracies)
            min_acc = np.min(accuracies)
            max_acc = np.max(accuracies)
            median_acc = np.median(accuracies)
            
            stats_text += f"{model}:\n"
            stats_text += f"  Mean: {mean_acc:.2f}%\n"
            stats_text += f"  Std Dev: {std_acc:.2f}%\n"
            stats_text += f"  Min: {min_acc:.2f}%\n"
            stats_text += f"  Max: {max_acc:.2f}%\n"
            stats_text += f"  Median: {median_acc:.2f}%\n\n"
        
        ax4.text(0.1, 0.9, stats_text, transform=ax4.transAxes, fontsize=10,
                verticalalignment='top', fontfamily='monospace')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"Box plots saved to: {save_path}")
    
    def create_detailed_analysis(self, save_path='detailed_model_analysis.png'):
        """Create detailed analysis with individual model performance"""
        if not self.data:
            print("No data to analyze!")
            return
        
        df = pd.DataFrame(self.data)
        
        # Create a larger figure for detailed analysis
        fig, axes = plt.subplots(2, 1, figsize=(16, 12))
        
        # 1. Individual model performance with error bars
        ax1 = axes[0]
        base_models = df['base_model'].unique()
        x_pos = np.arange(len(base_models))
        
        means = []
        stds = []
        mins = []
        maxs = []
        
        for model in base_models:
            model_data = df[df['base_model'] == model]['accuracy']
            means.append(model_data.mean())
            stds.append(model_data.std())
            mins.append(model_data.min())
            maxs.append(model_data.max())
        
        # Plot means with error bars
        bars = ax1.bar(x_pos, means, yerr=stds, capsize=5, alpha=0.7, 
                      color=plt.cm.Set3(np.linspace(0, 1, len(base_models))))
        
        # Add individual data points
        for i, model in enumerate(base_models):
            model_data = df[df['base_model'] == model]['accuracy']
            x_jitter = np.random.normal(i, 0.05, len(model_data))
            ax1.scatter(x_jitter, model_data, alpha=0.6, s=50, color='red')
        
        ax1.set_xlabel('Model')
        ax1.set_ylabel('Accuracy (%)')
        ax1.set_title('Model Performance with Standard Deviation', fontweight='bold')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(base_models, rotation=45)
        ax1.grid(True, alpha=0.3)
        
        # 2. Performance comparison table
        ax2 = axes[1]
        ax2.axis('off')
        
        # Create comparison table
        comparison_data = []
        for model in base_models:
            model_data = df[df['base_model'] == model]['accuracy']
            comparison_data.append({
                'Model': model,
                'Mean': f"{model_data.mean():.2f}%",
                'Std Dev': f"{model_data.std():.2f}%",
                'Min': f"{model_data.min():.2f}%",
                'Max': f"{model_data.max():.2f}%",
                'Runs': len(model_data)
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Create table
        table = ax2.table(cellText=comparison_df.values,
                         colLabels=comparison_df.columns,
                         cellLoc='center',
                         loc='center',
                         bbox=[0, 0, 1, 1])
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        
        # Style the table
        for i in range(len(comparison_df.columns)):
            table[(0, i)].set_facecolor('#40466e')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        ax2.set_title('Detailed Performance Comparison', fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"Detailed analysis saved to: {save_path}")
    
    def print_summary(self):
        """Print a summary of the analysis"""
        if not self.data:
            print("No data to summarize!")
            return
        
        print("\n" + "="*60)
        print("MODEL PERFORMANCE ANALYSIS SUMMARY")
        print("="*60)
        
        df = pd.DataFrame(self.data)
        
        for model in df['base_model'].unique():
            model_data = df[df['base_model'] == model]['accuracy']
            print(f"\n{model}:")
            print(f"  Runs: {len(model_data)}")
            print(f"  Accuracy: {model_data.tolist()}")
            print(f"  Mean: {model_data.mean():.2f}%")
            print(f"  Std Dev: {model_data.std():.2f}%")
            print(f"  Range: {model_data.min():.2f}% - {model_data.max():.2f}%")
            if model_data.mean() > 0:
                print(f"  Coefficient of Variation: {(model_data.std()/model_data.mean()*100):.2f}%")
            else:
                print(f"  Coefficient of Variation: N/A (mean is 0)")

def main():
    # Raw data from the user
    raw_data = """CO_CSV_ANCHORED_gpt-4o-mini_prompt18_run1	29	26	3	0	89.66%	10.34%
CO_CSV_ANCHORED_gpt-4o-mini_prompt18_run2	29	26	3	0	89.66%	10.34%
CO_CSV_ANCHORED_gpt-4o-mini_prompt18_run3	29	27	2	0	93.10%	6.90%
CO_CSV_ANCHORED_gpt-4o_prompt18_run1	29	11	18	0	37.93%	62.07%	0.00%
CO_CSV_ANCHORED_gpt-4o_prompt18_run2	29	11	18	0	37.93%	62.07%	0.00%
CO_CSV_ANCHORED_gpt-4o_prompt18_run3	29	10	19	0	34.48%	65.52%	0.00%
CO_CSV_ANCHORED_deepseek-r1-14b_Prompt17_1(72.41%)	29	21	8	0	72.41%	27.59%
CO_CSV_ANCHORED_deepseek-r1-14b_Prompt17_2(51.72%)	29	15	14	0	51.72%	48.28%
CO_CSV_ANCHORED_deepseek-r1-14b_Prompt17_3(48.28%)	29	14	15	0	48.28%	51.72%
CO_CSV_ANCHORED_mistral-7b_Prompt17_1 (11-30)	29	10	19	0	34.48%	65.52%	0.00%
CO_CSV_ANCHORED_mistral-7b_Prompt17_2 (9-30)	29	8	21	0	27.59%	72.41%	0.00%
CO_CSV_ANCHORED_mistral-7b_Prompt17_3 (15-30)	29	14	15	0	48.28%	51.72%	0.00%"""
    
    # Create analyzer and process data
    analyzer = ModelPerformanceAnalyzer()
    analyzer.parse_model_data(raw_data)
    
    # Generate visualizations
    print("Generating box plots...")
    analyzer.create_box_plots()
    
    print("\nGenerating detailed analysis...")
    analyzer.create_detailed_analysis()
    
    # Print summary
    analyzer.print_summary()

if __name__ == "__main__":
    main()
