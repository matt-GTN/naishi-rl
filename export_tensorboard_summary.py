#!/usr/bin/env python3
"""Export TensorBoard logs to LLM-friendly text summary."""

import os
from pathlib import Path
from tensorboard.backend.event_processing import event_accumulator

def export_run_summary(log_dir, output_file):
    """Export TensorBoard run data to a text summary."""
    
    with open(output_file, 'w') as f:
        f.write("# TensorBoard Training Summary\n\n")
        
        # Process each run directory
        for run_dir in sorted(Path(log_dir).iterdir()):
            if not run_dir.is_dir():
                continue
                
            f.write(f"## Run: {run_dir.name}\n\n")
            
            try:
                ea = event_accumulator.EventAccumulator(str(run_dir))
                ea.Reload()
                
                # Export scalar metrics
                if ea.Tags()['scalars']:
                    f.write("### Metrics\n\n")
                    
                    for tag in sorted(ea.Tags()['scalars']):
                        events = ea.Scalars(tag)
                        
                        if not events:
                            continue
                            
                        f.write(f"**{tag}**\n")
                        f.write(f"- Total steps: {len(events)}\n")
                        
                        values = [e.value for e in events]
                        f.write(f"- Initial: {values[0]:.4f}\n")
                        f.write(f"- Final: {values[-1]:.4f}\n")
                        f.write(f"- Min: {min(values):.4f}\n")
                        f.write(f"- Max: {max(values):.4f}\n")
                        f.write(f"- Mean: {sum(values)/len(values):.4f}\n")
                        
                        # Sample key points
                        if len(events) > 10:
                            f.write(f"\nKey checkpoints:\n")
                            step_size = len(events) // 10
                            for i in range(0, len(events), step_size):
                                e = events[i]
                                f.write(f"  Step {e.step}: {e.value:.4f}\n")
                        else:
                            f.write(f"\nAll values:\n")
                            for e in events:
                                f.write(f"  Step {e.step}: {e.value:.4f}\n")
                        
                        f.write("\n")
                
            except Exception as e:
                f.write(f"Error processing run: {e}\n\n")
        
        f.write("\n---\nExport complete\n")

if __name__ == "__main__":
    log_dir = "tensorboard_logs"
    output_file = "tensorboard_summary.txt"
    
    export_run_summary(log_dir, output_file)
    print(f"Summary exported to {output_file}")
