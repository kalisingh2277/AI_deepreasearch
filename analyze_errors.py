import json
from collections import Counter
from datetime import datetime, timedelta
import sys
from typing import Dict, List, Any
import matplotlib.pyplot as plt
from pathlib import Path

def load_error_stats() -> Dict[str, Any]:
    """Load error statistics from the JSON file"""
    try:
        with open("error_statistics.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("No error statistics file found.")
        return None
    except json.JSONDecodeError:
        print("Error statistics file is corrupted.")
        return None

def load_error_logs() -> List[str]:
    """Load raw error logs"""
    try:
        with open("error_logs.txt", "r") as f:
            return f.readlines()
    except FileNotFoundError:
        print("No error logs file found.")
        return []

def analyze_errors():
    """Analyze error statistics and logs"""
    # Load data
    stats = load_error_stats()
    logs = load_error_logs()
    
    if not stats and not logs:
        print("No error data available for analysis.")
        return
    
    print("\n=== Error Analysis Report ===\n")
    
    if stats:
        print(f"Total Errors: {stats['total_errors']}")
        print(f"Last Updated: {stats['last_updated']}\n")
        
        print("Error Types Distribution:")
        for error_type, count in stats['error_types'].items():
            print(f"  {error_type}: {count} ({(count/stats['total_errors']*100):.1f}%)")
        
        # Analyze recent errors
        recent_errors = [
            error for error in stats['error_timeline']
            if datetime.fromisoformat(error['timestamp']) > datetime.now() - timedelta(hours=24)
        ]
        
        print(f"\nRecent Errors (Last 24h): {len(recent_errors)}")
        if recent_errors:
            recent_types = Counter(error['error_type'] for error in recent_errors)
            print("\nRecent Error Types:")
            for error_type, count in recent_types.most_common():
                print(f"  {error_type}: {count}")
        
        # Create error timeline visualization
        if stats['error_timeline']:
            create_error_timeline(stats['error_timeline'])
    
    if logs:
        print("\nRecent Error Log Entries:")
        for line in logs[-5:]:  # Show last 5 log entries
            print(f"  {line.strip()}")

def create_error_timeline(timeline: List[Dict[str, Any]]):
    """Create a visualization of error occurrences over time"""
    try:
        # Convert timestamps to datetime objects
        times = [datetime.fromisoformat(error['timestamp']) for error in timeline]
        error_types = [error['error_type'] for error in timeline]
        
        # Create the plot
        plt.figure(figsize=(12, 6))
        plt.plot(times, range(len(times)), 'r-')
        plt.scatter(times, range(len(times)), c='red', alpha=0.5)
        
        # Customize the plot
        plt.title('Error Timeline')
        plt.xlabel('Time')
        plt.ylabel('Cumulative Errors')
        plt.grid(True, alpha=0.3)
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        
        # Save the plot
        plt.tight_layout()
        plt.savefig('error_timeline.png')
        print("\nError timeline visualization saved as 'error_timeline.png'")
        
    except Exception as e:
        print(f"Could not create visualization: {str(e)}")

def main():
    """Main function to run error analysis"""
    analyze_errors()

if __name__ == "__main__":
    main() 