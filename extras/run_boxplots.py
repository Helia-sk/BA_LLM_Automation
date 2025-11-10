#!/usr/bin/env python3
"""
Simple runner script for the Model Performance Box Plot Generator
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_boxplots.txt"])
        print("✓ Requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing requirements: {e}")
        return False
    return True

def run_analysis():
    """Run the box plot analysis"""
    print("\nRunning Model Performance Box Plot Generator...")
    try:
        # Import and run the main analysis
        from model_performance_boxplots import main
        main()
        print("✓ Analysis completed successfully!")
        return True
    except Exception as e:
        print(f"✗ Error running analysis: {e}")
        return False

def main():
    """Main runner function"""
    print("="*60)
    print("MODEL PERFORMANCE BOX PLOT GENERATOR")
    print("="*60)
    
    # Check if requirements file exists
    if not os.path.exists("requirements_boxplots.txt"):
        print("✗ requirements_boxplots.txt not found!")
        return
    
    # Install requirements
    if not install_requirements():
        return
    
    # Run analysis
    if not run_analysis():
        return
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE!")
    print("Generated files:")
    print("- model_performance_boxplots.png")
    print("- detailed_model_analysis.png")
    print("="*60)

if __name__ == "__main__":
    main()







