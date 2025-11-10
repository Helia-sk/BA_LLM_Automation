#!/usr/bin/env python3
"""
Temperature Box Plot Generator

This script creates box plots from LaTeX boxplot data for temperature values.
It processes the provided LaTeX data and generates two box plot diagrams.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def create_temperature_boxplots():
    """Create a single combined box plot for temperature data from actual run data"""
    
    # Actual data from the 3 runs
    # Temperature 0.2 (%): Run 1=46.43, Run 2=42.86, Run 3=46.43
    # Temperature 0.7 (%): Run 1=38.46, Run 2=21.43, Run 3=42.86
    
    # Create a single figure
    plt.figure(figsize=(10, 6))
    plt.title('Temperature Distribution Comparison (3 Runs)', fontsize=16, fontweight='bold')
    
    # Actual data from the runs
    temp_02_values = [46.43, 42.86, 46.43]  # Temperature 0.2 across 3 runs
    temp_07_values = [38.46, 21.43, 42.86]  # Temperature 0.7 across 3 runs
    
    # Calculate actual statistics
    temp_02_stats = {
        'mean': np.mean(temp_02_values),
        'median': np.median(temp_02_values),
        'std': np.std(temp_02_values),
        'min': np.min(temp_02_values),
        'max': np.max(temp_02_values),
        'q1': np.percentile(temp_02_values, 25),
        'q3': np.percentile(temp_02_values, 75),
        'iqr': np.percentile(temp_02_values, 75) - np.percentile(temp_02_values, 25)
    }
    
    temp_07_stats = {
        'mean': np.mean(temp_07_values),
        'median': np.median(temp_07_values),
        'std': np.std(temp_07_values),
        'min': np.min(temp_07_values),
        'max': np.max(temp_07_values),
        'q1': np.percentile(temp_07_values, 25),
        'q3': np.percentile(temp_07_values, 75),
        'iqr': np.percentile(temp_07_values, 75) - np.percentile(temp_07_values, 25)
    }
    
    # Create combined box plot
    data_to_plot = [temp_02_values, temp_07_values]
    labels = ['Temperature 0.2', 'Temperature 0.7']
    
    box_plot = plt.boxplot(data_to_plot, labels=labels, patch_artist=True)
    
    # Color the boxes
    colors = ['lightblue', 'lightcoral']
    for patch, color in zip(box_plot['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    plt.ylabel('Value', fontsize=12)
    plt.xlabel('Temperature Setting', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.ylim(20, 50)
    
    # Add statistics text
    stats_text = f"Temperature 0.2:\n  Mean: {temp_02_stats['mean']:.2f}\n  Median: {temp_02_stats['median']:.2f}\n  Std: {temp_02_stats['std']:.2f}\n\n"
    stats_text += f"Temperature 0.7:\n  Mean: {temp_07_stats['mean']:.2f}\n  Median: {temp_07_stats['median']:.2f}\n  Std: {temp_07_stats['std']:.2f}"
    
    plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
             verticalalignment='top', fontsize=10, 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('temperature_boxplots.png', dpi=300, bbox_inches='tight')
    # plt.show()  # Commented out to avoid interactive display
    
    print("Combined temperature box plot saved as 'temperature_boxplots.png'")
    
    # Print summary statistics
    print("\nTemperature Data Summary (3 Runs):")
    print("=" * 50)
    print("Temperature 0.2:")
    print(f"  Raw Data: {temp_02_values}")
    print(f"  Mean: {temp_02_stats['mean']:.2f}")
    print(f"  Median: {temp_02_stats['median']:.2f}")
    print(f"  Std Dev: {temp_02_stats['std']:.2f}")
    print(f"  Min: {temp_02_stats['min']:.2f}")
    print(f"  Max: {temp_02_stats['max']:.2f}")
    print(f"  Q1: {temp_02_stats['q1']:.2f}")
    print(f"  Q3: {temp_02_stats['q3']:.2f}")
    print(f"  IQR: {temp_02_stats['iqr']:.2f}")
    
    print("\nTemperature 0.7:")
    print(f"  Raw Data: {temp_07_values}")
    print(f"  Mean: {temp_07_stats['mean']:.2f}")
    print(f"  Median: {temp_07_stats['median']:.2f}")
    print(f"  Std Dev: {temp_07_stats['std']:.2f}")
    print(f"  Min: {temp_07_stats['min']:.2f}")
    print(f"  Max: {temp_07_stats['max']:.2f}")
    print(f"  Q1: {temp_07_stats['q1']:.2f}")
    print(f"  Q3: {temp_07_stats['q3']:.2f}")
    print(f"  IQR: {temp_07_stats['iqr']:.2f}")

def create_combined_temperature_plot():
    """Create a combined box plot showing both temperature distributions"""
    
    # Create synthetic data based on the boxplot statistics
    # For a proper box plot, we need to simulate the underlying data distribution
    
    # Temperature 0.2: very narrow distribution (all values close to 46.43)
    temp_02_values = np.random.normal(46.43, 0.5, 100)  # Small variance since all stats are similar
    
    # Temperature 0.7: wider distribution (range from 21.43 to 42.86)
    temp_07_values = np.random.normal(32.15, 5.0, 100)  # Mean between lower and upper quartile
    temp_07_values = np.clip(temp_07_values, 21.43, 42.86)  # Clip to whisker range
    
    # Create the combined plot
    plt.figure(figsize=(10, 6))
    
    # Create box plot data
    data_to_plot = [temp_02_values, temp_07_values]
    labels = ['Temperature 0.2', 'Temperature 0.7']
    
    # Create box plot
    box_plot = plt.boxplot(data_to_plot, labels=labels, patch_artist=True)
    
    # Color the boxes
    colors = ['lightblue', 'lightcoral']
    for patch, color in zip(box_plot['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    plt.title('Temperature Distribution Comparison', fontsize=14, fontweight='bold')
    plt.ylabel('Value', fontsize=12)
    plt.xlabel('Temperature Setting', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Add statistics text
    stats_text = f"Temperature 0.2:\n  Mean: {np.mean(temp_02_values):.2f}\n  Std: {np.std(temp_02_values):.2f}\n\n"
    stats_text += f"Temperature 0.7:\n  Mean: {np.mean(temp_07_values):.2f}\n  Std: {np.std(temp_07_values):.2f}"
    
    plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
             verticalalignment='top', fontsize=10, 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('temperature_comparison_boxplot.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Combined temperature comparison saved as 'temperature_comparison_boxplot.png'")

if __name__ == "__main__":
    print("Creating combined temperature box plot...")
    create_temperature_boxplots()
    
    print("\nBox plot generation complete!")
