import re
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend

import matplotlib.pyplot as plt

def process_log(log_data):
    # Regex patterns for extracting times
    insert_pattern_c = r"C-RBTree-Benchmark: Time to insert \d+ elements: (\d+) ms"
    remove_pattern_c = r"C-RBTree-Benchmark: Time to delete all the elements: (\d+) ms"
    iterate_pattern_c = r"C-RBTree-Benchmark: Time to iterate over the rbtree: (\d+) ms"

    insert_pattern_rust = r"Rust_RBTree_Benchmark: Time to insert \d+ elements: (\d+) ms"
    remove_pattern_rust = r"Rust_RBTree_Benchmark: Time to remove all elements: (\d+) ms"
    iterate_pattern_rust = r"Rust_RBTree_Benchmark: Time to iterate over the rbtree: (\d+) ms"

    # Extract times using regex
    insert_times_c = [int(m.group(1)) for m in re.finditer(insert_pattern_c, log_data)]
    remove_times_c = [int(m.group(1)) for m in re.finditer(remove_pattern_c, log_data)]
    iterate_times_c = [int(m.group(1)) for m in re.finditer(iterate_pattern_c, log_data)]

    insert_times_rust = [int(m.group(1)) for m in re.finditer(insert_pattern_rust, log_data)]
    remove_times_rust = [int(m.group(1)) for m in re.finditer(remove_pattern_rust, log_data)]
    iterate_times_rust = [int(m.group(1)) for m in re.finditer(iterate_pattern_rust, log_data)]

    return insert_times_c, remove_times_c, iterate_times_c, insert_times_rust, remove_times_rust, iterate_times_rust

def plot_statistics(insert_c, remove_c, iterate_c, insert_rust, remove_rust, iterate_rust):
    # Calculate statistics
    datasets = {
        "C Insert": insert_c,
        "C Remove": remove_c,
        "C Iterate": iterate_c,
        "Rust Insert": insert_rust,
        "Rust Remove": remove_rust,
        "Rust Iterate": iterate_rust,
    }

    stats = {name: (np.mean(data), np.min(data), np.max(data)) for name, data in datasets.items()}

    # Print statistics
    for name, (mean, min_val, max_val) in stats.items():
        print(f"\n{name} Statistics:")
        print(f"Mean: {mean:.2f} ms, Min: {min_val} ms, Max: {max_val} ms")

    # Plot histograms for Insert, Remove, and Iterate separately
    def plot_individual_metric(metric_name, c_data, rust_data, file_name):
        labels = ['C', 'Rust']
        mean_vals = [np.mean(c_data), np.mean(rust_data)]
        min_vals = [np.min(c_data), np.min(rust_data)]
        max_vals = [np.max(c_data), np.max(rust_data)]

        x = np.arange(len(labels))
        width = 0.25

        plt.figure(figsize=(10, 6))
        bars_min = plt.bar(x - width, min_vals, width, label='Min', color='skyblue')
        bars_mean = plt.bar(x, mean_vals, width, label='Mean', color='limegreen')
        bars_max = plt.bar(x + width, max_vals, width, label='Max', color='orange')

        # Add labels to bars
        for bars, values in zip([bars_min, bars_mean, bars_max], [min_vals, mean_vals, max_vals]):
            for bar, value in zip(bars, values):
                plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f"{value:.2f}",
                         ha='center', va='bottom', fontsize=10)

        plt.title(f"{metric_name} Time Comparison: C vs Rust")
        plt.ylabel("Time (ms)")
        plt.xticks(x, labels)
        plt.legend()
        plt.tight_layout()
        plt.savefig(file_name)
        print(f"Plot saved as '{file_name}'")

    # Generate plots for Insert, Remove, and Iterate
    plot_individual_metric("Insert", insert_c, insert_rust, "rbtree_insert_comparison.png")
    plot_individual_metric("Remove", remove_c, remove_rust, "rbtree_remove_comparison.png")
    plot_individual_metric("Iterate", iterate_c, iterate_rust, "rbtree_iterate_comparison.png")

# Main function
if __name__ == "__main__":
    with open("log.txt", "r") as f:
        log_data = f.read()

    insert_c, remove_c, iterate_c, insert_rust, remove_rust, iterate_rust = process_log(log_data)
    plot_statistics(insert_c, remove_c, iterate_c, insert_rust, remove_rust, iterate_rust)
