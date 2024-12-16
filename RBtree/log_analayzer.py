import re
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend

import matplotlib.pyplot as plt

def process_log(log_data):
    # Regex patterns for extracting times for C and Rust
    c_insert_pattern = r"C-RBTree-Benchmark: Time to insert \d+ elements: (\d+) ms"
    c_delete_pattern = r"C-RBTree-Benchmark: Time to delete all the elements: (\d+) ms"
    rust_insert_pattern = r"Rust_RBTree_Benchmark: Time to insert \d+ elements: (\d+) ms"
    rust_delete_pattern = r"Rust_RBTree_Benchmark: Time to remove all elements: (\d+) ms"

    # Extract times using regex
    c_insert_times = [int(m.group(1)) for m in re.finditer(c_insert_pattern, log_data)]
    c_delete_times = [int(m.group(1)) for m in re.finditer(c_delete_pattern, log_data)]
    rust_insert_times = [int(m.group(1)) for m in re.finditer(rust_insert_pattern, log_data)]
    rust_delete_times = [int(m.group(1)) for m in re.finditer(rust_delete_pattern, log_data)]

    return c_insert_times, c_delete_times, rust_insert_times, rust_delete_times

def calculate_statistics(data):
    return np.mean(data), np.min(data), np.max(data)

def plot_histogram(c_stats, rust_stats, title, filename):
    labels = ["Min", "Avg", "Max"]
    c_values = [c_stats[1], c_stats[0], c_stats[2]]  # Min, Avg, Max
    rust_values = [rust_stats[1], rust_stats[0], rust_stats[2]]  # Min, Avg, Max

    x = np.arange(len(labels))
    width = 0.3

    plt.figure(figsize=(10, 6))
    plt.bar(x - width / 2, c_values, width, label="C", color="skyblue")
    plt.bar(x + width / 2, rust_values, width, label="Rust", color="orange")

    # Annotate the bars with values
    for i, v in enumerate(c_values):
        plt.text(i - width / 2, v + 10, f"{v:.1f}", ha="center", va="bottom")
    for i, v in enumerate(rust_values):
        plt.text(i + width / 2, v + 10, f"{v:.1f}", ha="center", va="bottom")

    # Customization
    plt.xlabel("Metric")
    plt.ylabel("Time (ms)")
    plt.title(title)
    plt.xticks(x, labels)
    plt.legend()
    plt.tight_layout()

    # Save the plot
    plt.savefig(filename)
    print(f"Plot saved as '{filename}'")

# Main function
if __name__ == "__main__":
    # Read the log file
    log_file_path = "log.txt"  # Replace with the actual path
    with open(log_file_path, "r") as file:
        log_data = file.read()

    # Process the log data
    c_insert_times, c_delete_times, rust_insert_times, rust_delete_times = process_log(log_data)

    # Calculate statistics
    c_insert_stats = calculate_statistics(c_insert_times)
    c_delete_stats = calculate_statistics(c_delete_times)
    rust_insert_stats = calculate_statistics(rust_insert_times)
    rust_delete_stats = calculate_statistics(rust_delete_times)

    # Print statistics
    print("\nC Insert Statistics (Avg, Min, Max):", c_insert_stats)
    print("Rust Insert Statistics (Avg, Min, Max):", rust_insert_stats)
    print("\nC Delete Statistics (Avg, Min, Max):", c_delete_stats)
    print("Rust Delete Statistics (Avg, Min, Max):", rust_delete_stats)

    # Generate plots
    plot_histogram(c_insert_stats, rust_insert_stats, "RBTree Insertion Times", "rbtree_insertion.png")
    plot_histogram(c_delete_stats, rust_delete_stats, "RBTree Deletion Times", "rbtree_deletion.png")
