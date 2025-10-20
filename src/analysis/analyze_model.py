#!/usr/bin/env python3
"""
Quick script to analyze a Naishi model and generate comprehensive reports.
"""
from src.analysis.model_analytics import analyze_model
import sys

if __name__ == "__main__":
    # Default to the latest model
    model_path = "models/naishi_model"
    num_games = 100
    
    if len(sys.argv) > 1:
        model_path = sys.argv[1]
    if len(sys.argv) > 2:
        num_games = int(sys.argv[2])
    
    print(f"Analyzing model: {model_path}")
    print(f"Number of games: {num_games}")
    print("-" * 50)
    
    report_dir = analyze_model(model_path, num_games)
    
    print("\n" + "=" * 50)
    print("✓ Analysis Complete!")
    print("=" * 50)
    print(f"\nOpen this file in your browser:")
    print(f"  {report_dir}/index.html")
    print("\nAll interactive charts are available in the report.")
