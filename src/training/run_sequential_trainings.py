#!/usr/bin/env python3
"""
Run training script multiple times sequentially.
"""
import subprocess
import sys
from datetime import datetime

NUM_RUNS = 10

def run_training(run_number):
    """Run a single training iteration."""
    print(f"\n{'='*60}")
    print(f"Starting training run {run_number} of {NUM_RUNS}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    try:
        # Run the training script
        result = subprocess.run(
            ['python3', 'train_main_agent.py'],
            check=True,  # Raises exception if return code != 0
            capture_output=False  # Show output in real-time
        )
        
        print(f"\n✓ Training run {run_number} completed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Training run {run_number} failed with error code {e.returncode}")
        return False
    except KeyboardInterrupt:
        print(f"\n\n⚠ Training interrupted by user")
        return False

def main():
    """Main execution loop."""
    print("Starting sequential training runs...")
    print(f"Total runs: {NUM_RUNS}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    start_time = datetime.now()
    successful_runs = 0
    
    for i in range(1, NUM_RUNS + 1):
        success = run_training(i)
        
        if success:
            successful_runs += 1
        else:
            print("\n⚠ Stopping execution due to failure")
            break
        
        print(f"Completed run {i} at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    print(f"\n{'='*60}")
    print("Training Summary")
    print(f"{'='*60}")
    print(f"Successful runs: {successful_runs}/{NUM_RUNS}")
    print(f"Total time: {duration}")
    print(f"Finished at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # Exit with appropriate code
    sys.exit(0 if successful_runs == NUM_RUNS else 1)

if __name__ == "__main__":
    main()