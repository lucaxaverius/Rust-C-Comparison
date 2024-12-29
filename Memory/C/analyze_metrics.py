import csv
import statistics
import os
import sys

# Function to load data from CSV
def load_csv(csv_file):
    data = {}
    with open(csv_file, mode='r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header
        for row in reader:
            func, event, num_values, *values = row
            num_values = int(num_values)  # Convert num_values to integer
            values = list(map(float, values))  # Convert values to floats
            if func not in data:
                data[func] = {}
            data[func][event] = values  # Store the list of values
    return data

# Function to calculate statistics
def calculate_statistics(data):
    stats = {}
    for func, events in data.items():
        stats[func] = {}
        for event, values in events.items():
            stats[func][event] = {
                "avg": statistics.mean(values),
                "min": min(values),
                "max": max(values),
                "median": statistics.median(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0
            }
    return stats

# Function to save summary to a text file
def save_summary(stats, output_file):
    with open(output_file, "w") as f:
        for func, events in stats.items():
            f.write(f"Function: {func}\n")
            for event, stat in events.items():
                f.write(f"  Event: {event}\n")
                f.write(f"    Avg: {stat['avg']:.2f}\n")
                f.write(f"    Min: {stat['min']:.2f}\n")
                f.write(f"    Max: {stat['max']:.2f}\n")
                f.write(f"    Median: {stat['median']:.2f}\n")
                f.write(f"    Std Dev: {stat['std_dev']:.2f}\n")
            f.write("\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 analyze_metrics.py <input_csv> <output_summary>")
        sys.exit(1)

    csv_file = sys.argv[1]
    summary_file = sys.argv[2]

    data = load_csv(csv_file)
    stats = calculate_statistics(data)
    save_summary(stats, summary_file)
    print(f"Summary saved to {summary_file}")
