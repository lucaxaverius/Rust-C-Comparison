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

# Plot execution time violin plots
def plot_execution_time_violin(results, output_dir):
    operations = ["insert_front", "insert_back", "iterate", "remove"]
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
    # Filter out zero values for min
    for func_metrics in metrics.values():
        for event_metrics in func_metrics.values():
            if "Min" in event_metrics and event_metrics["Min"] == 0:
                del event_metrics["Min"]  # Remove invalid zero values
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

    # Helper to filter valid stats for plotting
    def filter_stats(stats):
        return [stats.get("Min", float("inf")), stats.get("Max", float("-inf")), stats.get("Median", float("nan"))]

    # Generate plots for C metrics
    for event in sorted(all_events):
        plt.figure(figsize=(10, 6))

        data = []
        labels = []

        for func in OPERATIONS:
            if func in c_metrics and event in c_metrics[func]:
                stats = c_metrics[func][event]
                data.append(filter_stats(stats))
                labels.append(func)

        # Create boxplot for C
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
                data.append(filter_stats(stats))
                labels.append(func)

        # Create boxplot for Rust
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


def plot_comparison_metrics(c_metrics, rust_metrics, output_dir):
    """
    Plots comparison metrics for each operation and metric, showing results for both
    the C and Rust implementations.

    Args:
        c_metrics (dict): Metrics for C implementation.
        rust_metrics (dict): Metrics for Rust implementation.
        output_dir (str): Directory where plots will be saved.
    """
    import matplotlib.pyplot as plt
    import os

    os.makedirs(output_dir, exist_ok=True)

    # Iterate over operations
    for operation in OPERATIONS:
        if operation not in c_metrics and operation not in rust_metrics:
            continue  # Skip if the operation is not present in either implementation

        metrics_to_plot = set()
        if operation in c_metrics:
            metrics_to_plot.update(c_metrics[operation].keys())
        if operation in rust_metrics:
            metrics_to_plot.update(rust_metrics[operation].keys())

        # Iterate over metrics for the current operation
        for metric in sorted(metrics_to_plot):
            plt.figure(figsize=(6, 4))  # Keep compact size for plots

            # Collect data for C implementation
            c_data = []
            if operation in c_metrics and metric in c_metrics[operation]:
                c_data = [
                    c_metrics[operation][metric].get("Min", float("inf")),
                    c_metrics[operation][metric].get("Median", float("nan")),
                    c_metrics[operation][metric].get("Max", float("-inf"))
                ]

            # Collect data for Rust implementation
            rust_data = []
            if operation in rust_metrics and metric in rust_metrics[operation]:
                rust_data = [
                    rust_metrics[operation][metric].get("Min", float("inf")),
                    rust_metrics[operation][metric].get("Median", float("nan")),
                    rust_metrics[operation][metric].get("Max", float("-inf"))
                ]

            # Combine data and labels for the plot
            data = [c_data, rust_data]
            labels = ["C", "Rust"]

            # Create boxplot
            box = plt.boxplot(
                data,
                patch_artist=True,
                widths=0.3,  # Narrower boxplots
                tick_labels=labels
            )

            # Customize colors
            colors = ["lightgrey", "lightblue"]
            for patch, color in zip(box['boxes'], colors):
                patch.set(facecolor=color)
            for median_line in box['medians']:
                median_line.set(color="black", linewidth=2)  # Median line black

            # Add labels and title with larger font sizes
            plt.title(
                f"Comparison of {metric} for {operation.replace('_', ' ').title()}",
                fontsize=14
            )
            plt.ylabel("Values (%)", fontsize=12)
            plt.xlabel("Implementation", fontsize=12)

            # Customize tick fonts
            plt.xticks(fontsize=12)
            plt.yticks(fontsize=12)

            # Add grid for better readability
            plt.grid(axis="y", linestyle="--", alpha=0.7)

            # Save plot
            plot_filename = f"{operation}_{metric}_comparison.png"
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, plot_filename), dpi=300)  # High DPI for clarity
            plt.close()


def plot_metric_comparison_across_operations(c_metrics, rust_metrics, output_dir):
    """
    Plots comparison metrics for each metric across all operations, showing results
    for both the C and Rust implementations.

    Args:
        c_metrics (dict): Metrics for C implementation.
        rust_metrics (dict): Metrics for Rust implementation.
        output_dir (str): Directory where plots will be saved.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Collect all unique metrics across C and Rust implementations
    all_metrics = set()
    for func_metrics in c_metrics.values():
        all_metrics.update(func_metrics.keys())
    for func_metrics in rust_metrics.values():
        all_metrics.update(func_metrics.keys())

    # Iterate over all unique metrics
    for metric in sorted(all_metrics):
        plt.figure(figsize=(10, 6))

        # Prepare data and labels for the plot
        data = []
        labels = []
        implementations = []

        # Collect data for each operation from C metrics
        for operation in OPERATIONS:
            if operation in c_metrics and metric in c_metrics[operation]:
                stats = c_metrics[operation][metric]
                data.append(stats.get("Median", float("nan")))  # Use Median for comparison
                labels.append(operation.replace("_", " ").title())
                implementations.append("C")

        # Collect data for each operation from Rust metrics
        for operation in OPERATIONS:
            if operation in rust_metrics and metric in rust_metrics[operation]:
                stats = rust_metrics[operation][metric]
                data.append(stats.get("Median", float("nan")))  # Use Median for comparison
                labels.append(operation.replace("_", " ").title())
                implementations.append("Rust")

        # Create bar plot
        df = pd.DataFrame({"Metric": labels, "Implementation": implementations, "Value": data})
        sns.barplot(
            data=df,
            x="Metric",
            y="Value",
            hue="Implementation",
            palette={"C": "lightgrey", "Rust": "lightblue"}
        )

        # Customize plot
        plt.title(f"Comparison of {metric} Across Operations")
        plt.ylabel("Median Value (%)")
        plt.xlabel("Operations")
        plt.xticks(rotation=45)
        plt.grid(axis="y", linestyle="--", alpha=0.7)

        # Save plot
        plot_filename = f"{metric}_comparison_across_operations.png"
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, plot_filename))
        plt.close()


def plot_metric_comparison_boxplot_across_operations(c_metrics, rust_metrics, output_dir):
    """
    Plots comparison metrics for each metric across all operations as a box plot,
    showing results for both the C and Rust implementations side by side for each function.

    Args:
        c_metrics (dict): Metrics for C implementation.
        rust_metrics (dict): Metrics for Rust implementation.
        output_dir (str): Directory where plots will be saved.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Collect all unique metrics across C and Rust implementations
    all_metrics = set()
    for func_metrics in c_metrics.values():
        all_metrics.update(func_metrics.keys())
    for func_metrics in rust_metrics.values():
        all_metrics.update(func_metrics.keys())

    # Iterate over all unique metrics
    for metric in sorted(all_metrics):
        plt.figure(figsize=(12, 8))

        data = []
        labels = []
        colors = []
        operation_positions = []  # To store positions for vertical lines

        # Collect data for each operation
        position = 0
        for operation in OPERATIONS:
            operation_positions.append(position + 0.5)  # Store the middle of the operation's positions

            # Add C implementation
            if operation in c_metrics and metric in c_metrics[operation]:
                stats = c_metrics[operation][metric]
                values = [
                    stats.get("Min", float("inf")),
                    stats.get("Median", float("nan")),
                    stats.get("Max", float("-inf"))
                ]
                data.append(values)
                labels.append(f"C-{operation.replace('_', ' ').title()}")
                colors.append("lightgrey")
                position += 1

            # Add Rust implementation
            if operation in rust_metrics and metric in rust_metrics[operation]:
                stats = rust_metrics[operation][metric]
                values = [
                    stats.get("Min", float("inf")),
                    stats.get("Median", float("nan")),
                    stats.get("Max", float("-inf"))
                ]
                data.append(values)
                labels.append(f"Rust-{operation.replace('_', ' ').title()}")
                colors.append("lightblue")
                position += 1

        # Create boxplot
        box = plt.boxplot(
            data,
            patch_artist=True,
            tick_labels=labels
        )

        # Customize colors
        for patch, color in zip(box['boxes'], colors):
            patch.set(facecolor=color)
        for median_line in box['medians']:
            median_line.set(color="black", linewidth=2)  # Median line black

        # Add vertical dashed lines to separate operations
        for xpos in operation_positions[:]:  # Exclude the last position
            plt.axvline(x=xpos, color="lightgrey", linestyle="--", linewidth=1, alpha=0.7)

        # Add legend
        plt.legend(
            handles=[
                plt.Line2D([0], [0], color="lightgrey", lw=4, label="C"),
                plt.Line2D([0], [0], color="lightblue", lw=4, label="Rust")
            ],
            loc="upper left",
            title="Legend"
        )

        # Add labels and title
        plt.title(f"Comparison of {metric} Across Operations")
        plt.ylabel("Values (%)")
        plt.xlabel("Operations")
        plt.xticks(rotation=45)
        plt.grid(axis="y", linestyle="--", alpha=0.7)

        # Save plot
        plot_filename = f"{metric}_comparison_across_operations.png"
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, plot_filename))
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
    plot_example_boxplot("./perf_metrics_plots")
    save_statistics_to_file(combined_results, "time-ex.txt")

    # Parse perf summary files
    c_metrics = parse_perf_summary(C_PERF_FILE)
    rust_metrics = parse_perf_summary(RUST_PERF_FILE)

    # Plot perf metrics box plots
    #plot_perf_metrics(c_metrics, rust_metrics, "./perf_metrics_plots")

    #plot_function_metrics(c_metrics, rust_metrics, "./perf_metrics_plots2")

    plot_comparison_metrics(c_metrics, rust_metrics, "./perf_metrics_plot3")

    #plot_metric_comparison_boxplot_across_operations(c_metrics, rust_metrics, "./perf_metrics_plot4")
