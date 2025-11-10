import matplotlib.pyplot as plt
import numpy as np

# Conversion accuracy per run (%)
data = {
    "DeepSeek-r1-14B": [70.00, 50.00, 46.67],
    "GPT-4o": [36.67, 36.67, 33.33],
    "GPT-4o-mini": [86.67, 86.67, 90.00],
    "Mistral-7B": [33.33, 26.67, 46.67]
}

# Create figure with single subplot
fig, ax = plt.subplots(1, 1, figsize=(10, 8))

# Prepare data for boxplot
model_names = list(data.keys())
values_list = list(data.values())

# Create boxplot with all models in one diagram
box_plot = ax.boxplot(values_list, 
                      labels=model_names,
                      vert=True, 
                      patch_artist=True,
                      boxprops=dict(facecolor='#cce5ff', color='#004080', linewidth=2),
                      medianprops=dict(color='red', linewidth=3),
                      whiskerprops=dict(color='#004080', linewidth=2),
                      capprops=dict(color='#004080', linewidth=2),
                      flierprops=dict(marker='o', markerfacecolor='red', markersize=6))

# Customize the plot
ax.set_ylabel("Conversion Accuracy (%)", fontsize=12)
ax.set_xlabel("Models", fontsize=12)
ax.set_title("Variance in Conversion Accuracy Across 3 Runs (CSV Logs)", fontsize=14, fontweight='bold')
ax.set_ylim(0, 100)
ax.grid(axis='y', linestyle='--', alpha=0.6)

# Rotate x-axis labels for better readability
plt.xticks(rotation=45, ha='right')

# Adjust layout to prevent label cutoff
plt.tight_layout()
plt.show()
