#!/usr/bin/env python3
"""
Compare multiple Naishi models side-by-side.
"""
from src.analysis.model_analytics import ModelAnalytics
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os
from datetime import datetime

def compare_models(model_paths, num_games=100):
    """
    Compare multiple models and generate a comparison report.
    
    Args:
        model_paths: List of paths to models to compare
        num_games: Number of games to play for each model
    """
    print(f"Comparing {len(model_paths)} models with {num_games} games each...")
    print("-" * 60)
    
    # Run analysis for each model
    all_analytics = []
    for i, model_path in enumerate(model_paths, 1):
        print(f"\n[{i}/{len(model_paths)}] Analyzing {os.path.basename(model_path)}...")
        analytics = ModelAnalytics(model_path, num_games)
        analytics.run_analysis()
        all_analytics.append((model_path, analytics))
    
    # Generate comparison report
    print("\nGenerating comparison report...")
    report_dir = _generate_comparison_report(all_analytics, num_games)
    
    return report_dir

def _generate_comparison_report(all_analytics, num_games):
    """Generate comparison charts."""
    output_dir = "analytics_reports"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_dir = os.path.join(output_dir, f"comparison_{timestamp}")
    os.makedirs(report_dir, exist_ok=True)
    
    model_names = [os.path.basename(path) for path, _ in all_analytics]
    
    # Create comparison charts
    _create_win_rate_comparison(all_analytics, model_names, report_dir)
    _create_score_comparison(all_analytics, model_names, report_dir)
    _create_action_comparison(all_analytics, model_names, report_dir)
    _create_strategy_comparison(all_analytics, model_names, report_dir)
    _create_card_preference_comparison(all_analytics, model_names, report_dir)
    
    # Create index
    _create_comparison_index(all_analytics, model_names, report_dir, num_games)
    
    return report_dir

def _create_win_rate_comparison(all_analytics, model_names, report_dir):
    """Compare win rates across models."""
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Win Rate Comparison', 'Average Score Difference'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}]]
    )
    
    win_rates = []
    score_diffs = []
    
    for _, analytics in all_analytics:
        total = analytics.stats['wins'] + analytics.stats['losses'] + analytics.stats['draws']
        win_rate = (analytics.stats['wins'] / total * 100) if total > 0 else 0
        win_rates.append(win_rate)
        score_diffs.append(np.mean(analytics.stats['score_differences']))
    
    # Win rates
    fig.add_trace(go.Bar(
        x=model_names,
        y=win_rates,
        marker=dict(color=win_rates, colorscale='RdYlGn', cmin=0, cmax=100,
                   line=dict(color='black', width=1)),
        text=[f"{wr:.1f}%" for wr in win_rates],
        textposition='outside'
    ), row=1, col=1)
    
    # Add baseline line
    fig.add_shape(
        type="line",
        x0=0, x1=1, y0=50, y1=50,
        xref="paper",
        line=dict(color="red", width=2, dash="dash"),
        row=1, col=1
    )
    
    # Score differences
    colors = ['#2ecc71' if sd > 0 else '#e74c3c' for sd in score_diffs]
    fig.add_trace(go.Bar(
        x=model_names,
        y=score_diffs,
        marker=dict(color=colors, line=dict(color='black', width=1)),
        text=[f"{sd:+.1f}" for sd in score_diffs],
        textposition='outside'
    ), row=1, col=2)
    
    # Add even line
    fig.add_shape(
        type="line",
        x0=0, x1=1, y0=0, y1=0,
        xref="paper",
        line=dict(color="red", width=2, dash="dash"),
        row=1, col=2
    )
    
    fig.update_layout(height=500, title_text="Performance Comparison", showlegend=False)
    fig.update_xaxes(tickangle=45)
    fig.write_html(os.path.join(report_dir, '01_win_rate_comparison.html'))

def _create_score_comparison(all_analytics, model_names, report_dir):
    """Compare score distributions."""
    fig = go.Figure()
    
    for name, analytics in zip(model_names, [a for _, a in all_analytics]):
        fig.add_trace(go.Box(
            y=analytics.stats['final_scores'],
            name=name,
            boxmean='sd'
        ))
    
    fig.update_layout(
        title="Score Distribution Comparison",
        yaxis_title="Final Score",
        height=600
    )
    fig.write_html(os.path.join(report_dir, '02_score_comparison.html'))

def _create_action_comparison(all_analytics, model_names, report_dir):
    """Compare action distributions."""
    action_names = ['Draft', 'Develop', 'Swap', 'Discard', 'Recall', 'Decree', 'End Game']
    
    fig = go.Figure()
    
    for name, analytics in zip(model_names, [a for _, a in all_analytics]):
        total = sum(analytics.stats['action_counts'].values())
        percentages = [analytics.stats['action_counts'].get(action, 0) / total * 100 
                      for action in action_names]
        
        fig.add_trace(go.Bar(
            name=name,
            x=action_names,
            y=percentages,
            text=[f"{p:.1f}%" for p in percentages],
            textposition='auto'
        ))
    
    fig.update_layout(
        title="Action Distribution Comparison",
        yaxis_title="Percentage (%)",
        barmode='group',
        height=600
    )
    fig.write_html(os.path.join(report_dir, '03_action_comparison.html'))

def _create_strategy_comparison(all_analytics, model_names, report_dir):
    """Compare strategic metrics."""
    metrics = []
    
    for _, analytics in all_analytics:
        total = analytics.stats['wins'] + analytics.stats['losses'] + analytics.stats['draws']
        win_rate = (analytics.stats['wins'] / total * 100) if total > 0 else 0
        
        avg_emissaries = np.mean(analytics.stats['emissary_usage_per_game']) if analytics.stats['emissary_usage_per_game'] else 0
        avg_length = np.mean(analytics.stats['game_lengths']) if analytics.stats['game_lengths'] else 0
        
        # Calculate action diversity
        action_counts = list(analytics.stats['action_counts'].values())
        total_actions = sum(action_counts)
        if total_actions > 0:
            probs = [c/total_actions for c in action_counts]
            entropy = -sum(p * np.log2(p) for p in probs if p > 0)
            max_entropy = np.log2(len(action_counts))
            diversity = (entropy / max_entropy * 100) if max_entropy > 0 else 0
        else:
            diversity = 0
        
        metrics.append({
            'win_rate': win_rate,
            'avg_emissaries': avg_emissaries,
            'avg_length': avg_length,
            'diversity': diversity
        })
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Win Rate', 'Emissary Usage', 'Game Length', 'Action Diversity')
    )
    
    # Win rate
    fig.add_trace(go.Bar(
        x=model_names,
        y=[m['win_rate'] for m in metrics],
        marker=dict(color='#2ecc71', line=dict(color='black', width=1)),
        text=[f"{m['win_rate']:.1f}%" for m in metrics],
        textposition='outside'
    ), row=1, col=1)
    
    # Emissary usage
    fig.add_trace(go.Bar(
        x=model_names,
        y=[m['avg_emissaries'] for m in metrics],
        marker=dict(color='#9b59b6', line=dict(color='black', width=1)),
        text=[f"{m['avg_emissaries']:.2f}" for m in metrics],
        textposition='outside'
    ), row=1, col=2)
    
    # Game length
    fig.add_trace(go.Bar(
        x=model_names,
        y=[m['avg_length'] for m in metrics],
        marker=dict(color='#3498db', line=dict(color='black', width=1)),
        text=[f"{m['avg_length']:.1f}" for m in metrics],
        textposition='outside'
    ), row=2, col=1)
    
    # Diversity
    fig.add_trace(go.Bar(
        x=model_names,
        y=[m['diversity'] for m in metrics],
        marker=dict(color='#f39c12', line=dict(color='black', width=1)),
        text=[f"{m['diversity']:.1f}%" for m in metrics],
        textposition='outside'
    ), row=2, col=2)
    
    fig.update_layout(height=800, title_text="Strategic Metrics Comparison", showlegend=False)
    fig.update_xaxes(tickangle=45)
    fig.write_html(os.path.join(report_dir, '04_strategy_comparison.html'))

def _create_card_preference_comparison(all_analytics, model_names, report_dir):
    """Compare card preferences."""
    fig = go.Figure()
    
    for name, analytics in zip(model_names, [a for _, a in all_analytics]):
        top_cards = analytics.stats['cards_in_final_line'].most_common(10)
        if top_cards:
            cards = [card for card, _ in top_cards]
            counts = [count for _, count in top_cards]
            
            fig.add_trace(go.Bar(
                name=name,
                x=cards,
                y=counts,
                text=counts,
                textposition='auto'
            ))
    
    fig.update_layout(
        title="Card Preference Comparison (Top 10 in Final Lines)",
        yaxis_title="Frequency",
        barmode='group',
        height=600
    )
    fig.write_html(os.path.join(report_dir, '05_card_preference_comparison.html'))

def _create_comparison_index(all_analytics, model_names, report_dir, num_games):
    """Create HTML index for comparison."""
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Naishi Model Comparison</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
        }}
        .models-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .model-card {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }}
        .chart-container {{
            margin: 20px 0;
            border: 2px solid #ecf0f1;
            border-radius: 8px;
            padding: 15px;
        }}
        iframe {{
            width: 100%;
            height: 600px;
            border: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 Naishi Model Comparison</h1>
        <p style="text-align: center; color: #7f8c8d;">
            Comparing {len(model_names)} models with {num_games} games each<br>
            Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        </p>
        
        <h2>Models Analyzed</h2>
        <div class="models-grid">
"""
    
    for i, (name, (_, analytics)) in enumerate(zip(model_names, all_analytics), 1):
        total = analytics.stats['wins'] + analytics.stats['losses'] + analytics.stats['draws']
        win_rate = (analytics.stats['wins'] / total * 100) if total > 0 else 0
        avg_score = np.mean(analytics.stats['final_scores'])
        
        html += f"""
            <div class="model-card">
                <h3>Model {i}: {name}</h3>
                <p><strong>Win Rate:</strong> {win_rate:.1f}%</p>
                <p><strong>Avg Score:</strong> {avg_score:.1f}</p>
                <p><strong>Games:</strong> {total}</p>
            </div>
"""
    
    html += """
        </div>
        
        <h2>Comparison Charts</h2>
        
        <div class="chart-container">
            <iframe src="01_win_rate_comparison.html"></iframe>
        </div>
        
        <div class="chart-container">
            <iframe src="02_score_comparison.html"></iframe>
        </div>
        
        <div class="chart-container">
            <iframe src="03_action_comparison.html"></iframe>
        </div>
        
        <div class="chart-container">
            <iframe src="04_strategy_comparison.html"></iframe>
        </div>
        
        <div class="chart-container">
            <iframe src="05_card_preference_comparison.html"></iframe>
        </div>
    </div>
</body>
</html>
"""
    
    with open(os.path.join(report_dir, 'index.html'), 'w') as f:
        f.write(html)

if __name__ == "__main__":
    import sys
    import glob
    
    if len(sys.argv) < 2:
        # Auto-detect all models
        model_files = glob.glob("models/naishi_model*.zip")
        if not model_files:
            print("No models found in models/ directory")
            print("Usage: python compare_models.py <model1> <model2> [model3...] [num_games]")
            sys.exit(1)
        
        # Remove .zip extension
        model_paths = [f[:-4] for f in sorted(model_files)]
        num_games = 100
        
        print(f"Auto-detected {len(model_paths)} models:")
        for path in model_paths:
            print(f"  - {path}")
    else:
        # Check if last arg is a number (num_games)
        try:
            num_games = int(sys.argv[-1])
            model_paths = sys.argv[1:-1]
        except ValueError:
            num_games = 100
            model_paths = sys.argv[1:]
    
    if len(model_paths) < 2:
        print("Need at least 2 models to compare")
        sys.exit(1)
    
    report_dir = compare_models(model_paths, num_games)
    
    print("\n" + "=" * 60)
    print("✓ Comparison Complete!")
    print("=" * 60)
    print(f"\nOpen this file in your browser:")
    print(f"  {report_dir}/index.html")
