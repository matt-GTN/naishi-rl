#!/usr/bin/env python3
"""
Convenience script to analyze a trained model.
Imports from src.analysis.analyze_model
"""
import sys
from src.analysis.model_analytics import analyze_model

if __name__ == "__main__":
    model_path = "models/naishi_model"
    num_games = 100
    
    if len(sys.argv) > 1:
        model_path = sys.argv[1]
    if len(sys.argv) > 2:
        num_games = int(sys.argv[2])
    
    print(f"Analyzing model: {model_path}")
    print(f"Number of games: {num_games}")
    
    analyze_model(model_path, num_games=num_games)
