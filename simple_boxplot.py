#!/usr/bin/env python3
"""
Simple Box Plot Generator for Model Performance Data
"""

import matplotlib.pyplot as plt

def create_model_boxplot():
    """Create box plot for model performance across 3 runs"""
    
    # Replace these with your 3-run values for each model
    data = {
        "Mistral-7B": [34.48, 27.59, 48.28],
        "DeepSeek-14B": [72.41, 51.72, 48.28],
        "GPT-4o": [37.93, 37.93, 34.48],
        "GPT-4o-mini": [89.66, 89.66, 93.10]
    }

    # Create the box plot
    plt.figure(figsize=(8, 10))
    box_plot = plt.boxplot(data.values(), labels=data.keys(), patch_artist=True, vert=True)
    
    # Color the boxes
    colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow']
    for patch, color in zip(box_plot['boxes'], colors):
        patch.set_facecolor(color)
    
    plt.title("Model Variance Across 3 Runs (Prompt 17)", fontsize=14, fontweight='bold')
    plt.ylabel("Accuracy (%)", fontsize=12)
    plt.xlabel("Model", fontsize=12)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    
    # Add some statistics as text
    stats_text = "Statistics:\n"
    for model, values in data.items():
        mean_val = sum(values) / len(values)
        std_val = (sum((x - mean_val) ** 2 for x in values) / len(values)) ** 0.5
        stats_text += f"{model}: {mean_val:.1f}% ± {std_val:.1f}%\n"
    
    plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
             verticalalignment='top', fontsize=9, 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('model_variance_boxplot.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Box plot saved as 'model_variance_boxplot.png'")
    
    # Print summary statistics
    print("\nModel Performance Summary:")
    print("=" * 50)
    for model, values in data.items():
        mean_val = sum(values) / len(values)
        std_val = (sum((x - mean_val) ** 2 for x in values) / len(values)) ** 0.5
        min_val = min(values)
        max_val = max(values)
        range_val = max_val - min_val
        
        print(f"{model}:")
        print(f"  Values: {values}")
        print(f"  Mean: {mean_val:.2f}%")
        print(f"  Std Dev: {std_val:.2f}%")
        print(f"  Range: {min_val:.2f}% - {max_val:.2f}%")
        print(f"  Coefficient of Variation: {(std_val/mean_val*100):.2f}%")
        print()

if __name__ == "__main__":
    create_model_boxplot()
