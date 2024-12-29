import os
import re
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

# Paths to log and summary files (set these before running the script)
C_LOG_FILE = "./C/logs/module_logs.txt"
RUST_LOG_FILE = "./Rust/logs/module_logs.txt"
C_PERF_FILE = "./C/results/summary.txt"
RUST_PERF_FILE = "./Rust/results/summary.txt"

# Functions for the four operations
OPERATIONS = ["insert_front", "insert_back", "iterate_all", "remove_all"]

# Patterns for extracting C and Rust metrics
patterns = {
    "c_insert_front": r"C-List-Benchmark: Time to insert \d+ elements at front: (\d+) ms",
    "c_insert_back": r"C-List-Benchmark: Time to insert \d+ elements at back: (\d+) ms",
    "c_iterate": r"C-List-Benchmark: Time to iterate \d+ elements: (\d+) ms",
    "c_remove": r"C-List-Benchmark: Time to remove all elements: (\d+) ms",
    
    "rust_insert_front": r"Rust_List_Benchmark: Time to insert \d+ elements at front: (\d+) ms",
    "rust_insert_back": r"Rust_List_Benchmark: Time to insert \d+ elements at back: (\d+) ms",
    "rust_iterate": r"Rust_List_Benchmark: Time to iterate \d+ elements: (\d+) ms",
    "rust_remove": r"Rust_List_Benchmark: Time to remove all elements: (\d+) ms",
}

# Extract metrics from logs
def extract_execution_times(log_file, patterns):
    results = {key: [] for key in patterns.keys()}
    with open(log_file, "r") as f:
        for line in f:
            for key, pattern in patterns.items():
                match = re.search(pattern, line)
                if match:
                    results[key].append(int(match.group(1)))
    return results

# Plot execution time box plots with mean and median
def plot_execution_time(results, output_dir):
    operations = ["insert_front", "insert_back", "iterate", "remove"]
    for operation in operations:
        c_key = f"c_{operation}"
        rust_key = f"rust_{operation}"
        
        plt.figure(figsize=(8, 6))  # Increased figure size for better readability
        data = [results[c_key], results[rust_key]]
        box = plt.boxplot(data, patch_artist=True, tick_labels=["C", "Rust"], showmeans=True, meanline=True)
        
        # Customize box plot colors
        for patch in box['boxes']:
            patch.set(facecolor="lightgrey")
        for median_line in box['medians']:
            median_line.set(color="black", linewidth=2)  # Median line black
        for mean_line in box['means']:
            mean_line.set(color="black", linestyle="--", linewidth=1.5)  # Mean line black dashed

        # Add labels and title
        plt.title(f"Execution Time Comparison: {operation.replace('_', ' ').title()}")
        plt.ylabel("Time (ms)")
        plt.xlabel("Implementation")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{operation}_execution_time.png"))
        plt.close()

# Generate an example box plot with annotations
def plot_example_boxplot(output_dir):
    data = [3, 4, 4, 5, 6, 8, 9]
    plt.figure(figsize=(6, 6))  # Maintain smaller size for the example plot
    box = plt.boxplot([data], patch_artist=True, showmeans=True, meanline=True)

    # Customize box plot colors
    for patch in box['boxes']:
        patch.set(facecolor="lightgrey")
    for median_line in box['medians']:
        median_line.set(color="black", linewidth=2)  # Median line black
    for mean_line in box['means']:
        mean_line.set(color="black", linestyle="--", linewidth=1.5)  # Mean line black dashed

    # Extract statistics for annotation
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    median = np.median(data)
    mean = np.mean(data)
    min_val = np.min(data)
    max_val = np.max(data)

    # Add annotations
    plt.text(1.15, q1, "Q1", va='center', ha='left', fontsize=9, color='black')
    plt.text(1.15, q3, "Q3", va='center', ha='left', fontsize=9, color='black')
    plt.text(1.15, median, "Median", va='center', ha='left', fontsize=9, color='black')
    plt.text(1.15, mean, "Mean", va='center', ha='left', fontsize=9, color='black')
    plt.text(1.15, min_val, "Min", va='center', ha='left', fontsize=9, color='black')
    plt.text(1.15, max_val, "Max", va='center', ha='left', fontsize=9, color='black')

    # Add labels
    plt.title("Example Box Plot with Annotations")
    plt.ylabel("Values")
    plt.xlabel("Example Data")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "example_boxplot.png"))
    plt.close()

# Parse perf summary files
def parse_perf_summary(summary_file):
    metrics = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    with open(summary_file, "r") as f:
        current_function = None
        current_event = None
        for line in f:
            if line.startswith("Function:"):
                current_function = line.split(":")[1].strip()
            elif line.startswith("  Event:"):
                current_event = line.split(":")[1].strip()
            elif current_function and current_event:
                match = re.search(r"(\w+): ([\d.]+)", line)
                if match:
                    stat, value = match.groups()
                    metrics[current_function][current_event][stat] = float(value)
    return metrics

# Plot perf metrics box plots for C and Rust separately
def plot_perf_metrics(c_metrics, rust_metrics, output_dir):
    c_output_dir = os.path.join(output_dir, "c_metrics")
    rust_output_dir = os.path.join(output_dir, "rust_metrics")
    os.makedirs(c_output_dir, exist_ok=True)
    os.makedirs(rust_output_dir, exist_ok=True)

    # Get all unique events
    all_events = set()
    for func_metrics in c_metrics.values():
        all_events.update(func_metrics.keys())
    for func_metrics in rust_metrics.values():
        all_events.update(func_metrics.keys())

    # Generate plots for C metrics
    for event in sorted(all_events):
        plt.figure(figsize=(10, 6))
        
        data = []
        labels = []

        for func in OPERATIONS:
            if func in c_metrics and event in c_metrics[func]:
                stats = c_metrics[func][event]
                data.append([stats["Min"], stats["Max"], stats["Median"], stats["Avg"], stats["Std Dev"]])
                labels.append(func)

        # Create boxplot for C
        box = plt.boxplot(
            data,
            patch_artist=True,
            showmeans=True,
            meanline=True,
            tick_labels=labels
        )

        # Customize colors
        for patch in box['boxes']:
            patch.set(facecolor="lightgrey")
        for median_line in box['medians']:
            median_line.set(color="black", linewidth=2)  # Median line black
        for mean_line in box['means']:
            mean_line.set(color="black", linestyle="--", linewidth=1.5)  # Mean line black dashed

        # Add labels and title
        plt.title(f"C Implementation - Perf Metrics for {event}")
        plt.ylabel("Values (%)")
        plt.xlabel("Functions")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(c_output_dir, f"{event}_c_metrics.png"))
        plt.close()

    # Generate plots for Rust metrics
    for event in sorted(all_events):
        plt.figure(figsize=(10, 6))
        
        data = []
        labels = []

        for func in OPERATIONS:
            if func in rust_metrics and event in rust_metrics[func]:
                stats = rust_metrics[func][event]
                data.append([stats["Min"], stats["Max"], stats["Median"], stats["Avg"], stats["Std Dev"]])
                labels.append(func)

        # Create boxplot for Rust
        box = plt.boxplot(
            data,
            patch_artist=True,
            showmeans=True,
            meanline=True,
            tick_labels=labels
        )

        # Customize colors
        for patch in box['boxes']:
            patch.set(facecolor="lightblue")
        for median_line in box['medians']:
            median_line.set(color="black", linewidth=2)  # Median line black
        for mean_line in box['means']:
            mean_line.set(color="black", linestyle="--", linewidth=1.5)  # Mean line black dashed

        # Add labels and title
        plt.title(f"Rust Implementation - Perf Metrics for {event}")
        plt.ylabel("Values (%)")
        plt.xlabel("Functions")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(rust_output_dir, f"{event}_rust_metrics.png"))
        plt.close()


if __name__ == "__main__":
    # Create output directories
    os.makedirs("./execution_time_plots", exist_ok=True)
    os.makedirs("./perf_metrics_plots", exist_ok=True)

    # Extract execution times
    c_results = extract_execution_times(C_LOG_FILE, {k: v for k, v in patterns.items() if k.startswith("c_")})
    rust_results = extract_execution_times(RUST_LOG_FILE, {k: v for k, v in patterns.items() if k.startswith("rust_")})


    # Combine results
    combined_results = {**c_results, **rust_results}

    # Plot execution time box plots
    plot_execution_time(combined_results, "./execution_time_plots")
    plot_example_boxplot("./execution_time_plots")
    # Parse perf summary files
    c_metrics = parse_perf_summary(C_PERF_FILE)
    rust_metrics = parse_perf_summary(RUST_PERF_FILE)

    # Plot perf metrics box plots
    plot_perf_metrics(c_metrics, rust_metrics, "./perf_metrics_plots")