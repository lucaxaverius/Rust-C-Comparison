import re
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt

def process_log(log_data):
    # Regex patterns for extracting times
    patterns = {
        "c_insert": r"C-RBTree-Benchmark: Time to insert \d+ elements: (\d+) ms",
        "c_remove": r"C-RBTree-Benchmark: Time to delete all the elements: (\d+) ms",
        "c_iterate": r"C-RBTree-Benchmark: Time to iterate over the rbtree: (\d+) ms",

        "rust_insert": r"Rust_RBTree_Benchmark: Time to insert \d+ elements: (\d+) ms",
        "rust_remove": r"Rust_RBTree_Benchmark: Time to remove all elements: (\d+) ms",
        "rust_iterate": r"Rust_RBTree_Benchmark: Time to iterate over the rbtree: (\d+) ms",
    }

    # Extract times using regex
    data = {key: [int(m.group(1)) for m in re.finditer(pattern, log_data)] for key, pattern in patterns.items()}

    # Print extracted data for verification
    for key, values in data.items():
        print(f"{key} Data: {values}")

    return data

def plot_comparison(data, metric_name, c_key, rust_key, filename):
    # Extract values for C and Rust
    c_values = data[c_key]
    rust_values = data[rust_key]

    # Calculate statistics
    c_stats = {"Min": np.min(c_values), "Avg": np.mean(c_values), "Max": np.max(c_values)}
    rust_stats = {"Min": np.min(rust_values), "Avg": np.mean(rust_values), "Max": np.max(rust_values)}

    # Print statistics for debugging
    print(f"\n{metric_name} Statistics:")
    print(f"C: Min={c_stats['Min']}, Avg={c_stats['Avg']:.2f}, Max={c_stats['Max']}")
    print(f"Rust: Min={rust_stats['Min']}, Avg={rust_stats['Avg']:.2f}, Max={rust_stats['Max']}")

    # Create bar plot
    labels = ["Min", "Avg", "Max"]
    c_values_plot = [c_stats[label] for label in labels]
    rust_values_plot = [rust_stats[label] for label in labels]

    x = np.arange(len(labels))
    width = 0.35

    plt.figure(figsize=(10, 6))
    bars_c = plt.bar(x - width / 2, c_values_plot, width, label="C", color="skyblue")
    bars_rust = plt.bar(x + width / 2, rust_values_plot, width, label="Rust", color="orange")

    # Annotate values on bars
    for bars, values in zip([bars_c, bars_rust], [c_values_plot, rust_values_plot]):
        for bar, value in zip(bars, values):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f"{value:.2f}",
                     ha='center', va='bottom', fontsize=10)

    # Customize plot
    plt.title(f"{metric_name} Time Comparison: C vs Rust")
    plt.ylabel("Time (ms)")
    plt.xticks(x, labels)
    plt.legend()
    plt.tight_layout()

    # Save the plot
    plt.savefig(filename)
    print(f"Plot saved as '{filename}'")

if __name__ == "__main__":
    # Read the log file
    with open("log.txt", "r") as file:
        log_data = file.read()

    # Process the log data
    data = process_log(log_data)

    # Generate comparison plots
    plot_comparison(data, "Insert", "c_insert", "rust_insert", "rbtree_insert_comparison.png")
    plot_comparison(data, "Remove", "c_remove", "rust_remove", "rbtree_remove_comparison.png")
    plot_comparison(data, "Iterate", "c_iterate", "rust_iterate", "rbtree_iterate_comparison.png")
