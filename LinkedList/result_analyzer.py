import re
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt

def process_log(log_data):
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
    
    # Extract data
    data = {key: [int(m.group(1)) for m in re.finditer(pattern, log_data)] for key, pattern in patterns.items()}

    # Print extracted data for debugging
    for key, values in data.items():
        print(f"{key} Data: {values}")

    return data

def calculate_statistics(values):
    return {
        "Min": np.min(values),
        "Avg": np.mean(values),
        "Max": np.max(values),
        "Var": np.var(values),
        "Median": np.median(values),
    }

def plot_comparison(data, metric_name, c_key, rust_key, filename):
    # Extract values
    c_values = data[c_key]
    rust_values = data[rust_key]
    
    # Calculate statistics
    c_stats = calculate_statistics(c_values)
    rust_stats = calculate_statistics(rust_values)
    
    # Print statistics for debugging
    print(f"\n{metric_name} Statistics:")
    print(f"C: {c_stats}")
    print(f"Rust: {rust_stats}")
    
    # Create bar plot
    labels = ["Min", "Avg", "Max", "Median"]
    c_plot_values = [c_stats[label] for label in labels]
    rust_plot_values = [rust_stats[label] for label in labels]

    x = np.arange(len(labels))
    width = 0.35

    plt.figure(figsize=(12, 8))
    bars_c = plt.bar(x - width / 2, c_plot_values, width, label="C", color="skyblue")
    bars_rust = plt.bar(x + width / 2, rust_plot_values, width, label="Rust", color="orange")

    # Annotate values on bars
    for bars, values in zip([bars_c, bars_rust], [c_plot_values, rust_plot_values]):
        for bar, value in zip(bars, values):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f"{value:.2f}",
                     ha='center', va='bottom', fontsize=10)

    # Add variance to the legend
    variance_c = f"(C) | Variance: {c_stats['Var']:.2f} ms²"
    variance_rust = f"(Rust) | Variance : {rust_stats['Var']:.2f} ms²"
    plt.legend([variance_c, variance_rust, "C", "Rust"], loc="upper right", fontsize=10)

    # Customize plot
    plt.title(f"{metric_name} Comparison: C vs Rust")
    plt.ylabel("Time (ms)")
    plt.xticks(x, labels, rotation=45)
    plt.tight_layout()

    # Save the plot
    plt.savefig(filename)
    print(f"Plot saved as '{filename}'")

if __name__ == "__main__":
    # Read log file
    with open("log.txt", "r") as file:
        log_data = file.read()

    # Process the log file
    data = process_log(log_data)

    # Generate comparison plots
    plot_comparison(data, "Insert Front", "c_insert_front", "rust_insert_front", "insert_front_comparison.png")
    plot_comparison(data, "Insert Back", "c_insert_back", "rust_insert_back", "insert_back_comparison.png")
    plot_comparison(data, "Iteration", "c_iterate", "rust_iterate", "iteration_comparison.png")
    plot_comparison(data, "Remove", "c_remove", "rust_remove", "remove_comparison.png")
