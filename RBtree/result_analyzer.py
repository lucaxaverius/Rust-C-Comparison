import os
import re
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import seaborn as sns
# Convert to DataFrame
import pandas as pd

# Paths to log and summary files (set these before running the script)
C_LOG_FILE = "./C/logs/module_logs.txt"
RUST_LOG_FILE = "./Rust/logs/module_logs.txt"
C_PERF_FILE = "./C/results/summary.txt"
RUST_PERF_FILE = "./Rust/results/summary.txt"

# Functions for the four operations
OPERATIONS = ["insert_values", "iterate_all", "remove_all"]

# Patterns for extracting C and Rust metrics
patterns = {
    "c_insert": r"C-RBTree-Benchmark: Time to insert \d+ elements: (\d+) ms",
    "c_iterate": r"C-RBTree-Benchmark: Time to iterate over the rbtree: (\d+) ms",
    "c_remove": r"C-RBTree-Benchmark: Time to delete all the elements: (\d+) ms",

    "rust_insert": r"Rust_RBTree_Benchmark: Time to insert \d+ elements: (\d+) ms",
    "rust_iterate": r"Rust_RBTree_Benchmark: Time to iterate over the rbtree: (\d+) ms",
    "rust_remove": r"Rust_RBTree_Benchmark: Time to remove all elements: (\d+) ms",

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



# Plot execution time violin plots
def plot_execution_time_violin(results, output_dir):
    operations = ["insert","iterate","remove"]
    for operation in operations:
        c_key = f"c_{operation}"
        rust_key = f"rust_{operation}"

        # Prepare data for violin plot
        data = []
        for value in results[c_key]:
            data.append({"Implementation": "C", "Time (ms)": value})
        for value in results[rust_key]:
            data.append({"Implementation": "Rust", "Time (ms)": value})

        df = pd.DataFrame(data)

        # Create violin plot
        plt.figure(figsize=(8, 6))
        sns.violinplot(
            x="Implementation",
            y="Time (ms)",
            data=df,
            palette={"C": "lightgrey", "Rust": "lightblue"},
            inner="quartile",
            hue="Implementation",
            legend=False,
        )

        # Customize plot
        plt.title(f"Execution Time Comparison: {operation.replace('_', ' ').title()}")
        plt.ylabel("Time (ms)")
        plt.xlabel("Implementation")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{operation}_execution_time_violin.png"))
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

# Function to calculate and save statistics to a file
def save_statistics_to_file(data, output_file):
    """
    Saves the mean, min, max, median, and standard deviation of the provided data to a file.

    Args:
        data (dict): A dictionary where keys are the operations (e.g., "c_insert_front")
                     and values are lists of times for each operation.
        output_file (str): Path to the output file to save the statistics.
    """
    with open(output_file, "w") as f:
        f.write("Operation Statistics:\n")
        f.write("-" * 50 + "\n")
        
        for operation, times in data.items():
            if times:  # Check if the operation has data
                mean = np.mean(times)
                min_val = np.min(times)
                max_val = np.max(times)
                median = np.median(times)
                std_dev = np.std(times)

                f.write(f"Operation: {operation}\n")
                f.write(f"  Mean: {mean:.2f} ms\n")
                f.write(f"  Min: {min_val} ms\n")
                f.write(f"  Max: {max_val} ms\n")
                f.write(f"  Median: {median} ms\n")
                f.write(f"  Std Dev: {std_dev:.2f} ms\n")
                f.write("-" * 50 + "\n")
            else:
                f.write(f"Operation: {operation}\n")
                f.write("  No data available.\n")
                f.write("-" * 50 + "\n")


# Plot all metrics for a single function
def plot_function_metrics(c_metrics, rust_metrics, output_dir):
    c_output_dir = os.path.join(output_dir, "c_function_metrics")
    rust_output_dir = os.path.join(output_dir, "rust_function_metrics")
    os.makedirs(c_output_dir, exist_ok=True)
    os.makedirs(rust_output_dir, exist_ok=True)

    def get_function_data(metrics, func):
        """Extracts data for all metrics of a single function."""
        data = []
        labels = []
        if func in metrics:
            for metric, stats in metrics[func].items():
                # Collect Min, Max, and Median values only
                values = [stats.get("Min", float("inf")), stats.get("Max", float("-inf")), stats.get("Median", float("nan"))]
                data.append(values)
                labels.append(metric)
        return data, labels

    # Generate plots for C functions
    for func in OPERATIONS:
        if func in c_metrics:
            plt.figure(figsize=(10, 6))

            data, labels = get_function_data(c_metrics, func)

            # Create boxplot
            box = plt.boxplot(
                data,
                patch_artist=True,
                tick_labels=labels
            )

            # Customize colors
            for patch in box['boxes']:
                patch.set(facecolor="lightgrey")
            for median_line in box['medians']:
                median_line.set(color="black", linewidth=2)  # Median line black

            # Add labels and title
            plt.title(f"C - {func.replace('_', ' ').title()} - Perf Metrics")
            plt.ylabel("Values (%)")
            plt.xlabel("Metrics")
            plt.grid(axis="y", linestyle="--", alpha=0.7)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(os.path.join(c_output_dir, f"{func}_c_metrics.png"))
            plt.close()

    # Generate plots for Rust functions
    for func in OPERATIONS:
        if func in rust_metrics:
            plt.figure(figsize=(10, 6))

            data, labels = get_function_data(rust_metrics, func)

            # Create boxplot
            box = plt.boxplot(
                data,
                patch_artist=True,
                tick_labels=labels
            )

            # Customize colors
            for patch in box['boxes']:
                patch.set(facecolor="lightblue")
            for median_line in box['medians']:
                median_line.set(color="black", linewidth=2)  # Median line black

            # Add labels and title
            plt.title(f"Rust - {func.replace('_', ' ').title()} - Perf Metrics")
            plt.ylabel("Values (%)")
            plt.xlabel("Metrics")
            plt.grid(axis="y", linestyle="--", alpha=0.7)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(os.path.join(rust_output_dir, f"{func}_rust_metrics.png"))
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
    plot_execution_time_violin(combined_results, "./execution_time_plots")
    save_statistics_to_file(combined_results, "./execution_time_plots/time-ex.txt")

    # Parse perf summary files
    c_metrics = parse_perf_summary(C_PERF_FILE)
    rust_metrics = parse_perf_summary(RUST_PERF_FILE)

    # Plot perf metrics box plots
    #plot_perf_metrics(c_metrics, rust_metrics, "./perf_metrics_plots")
    plot_function_metrics(c_metrics, rust_metrics, "./perf_metrics_plots")