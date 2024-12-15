import re
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend

import matplotlib.pyplot as plt

def process_log(log_data):
    # Regex patterns for extracting times
    insert_front_pattern = r"Time to insert \d+ elements at front: (\d+) ms"
    insert_back_pattern = r"Time to insert \d+ elements at back: (\d+) ms"
    remove_pattern = r"Time to remove all elements: (\d+) ms"

    # Extract times using regex
    insert_front_times = [int(m.group(1)) for m in re.finditer(insert_front_pattern, log_data)]
    insert_back_times = [int(m.group(1)) for m in re.finditer(insert_back_pattern, log_data)]
    remove_times = [int(m.group(1)) for m in re.finditer(remove_pattern, log_data)]

    # Print extracted data
    print("\nInsert Front Array:", insert_front_times)
    print("\nInsert Back Array:", insert_back_times)
    print("\nRemove Array:", remove_times)

    return insert_front_times, insert_back_times, remove_times

def plot_statistics(insert_front, insert_back, remove):
    # Calculate statistics
    datasets = {
        "Insert Front": insert_front,
        "Insert Back": insert_back,
        "Remove": remove,
    }
    
    stats = {name: (np.mean(data), np.min(data), np.max(data), np.std(data)) for name, data in datasets.items()}

    # Print statistics
    for name, (mean, min_val, max_val, std) in stats.items():
        print(f"\n{name} Statistics:")
        print(f"Mean: {mean:.2f} ms, Min: {min_val} ms, Max: {max_val} ms, Std Dev: {std:.2f} ms")

    # Plot graphs
    plt.figure(figsize=(12, 6))

    # Bar plot for means, mins, and maxs
    labels = list(stats.keys())
    means = [stats[name][0] for name in labels]
    mins = [stats[name][1] for name in labels]
    maxs = [stats[name][2] for name in labels]

    x = np.arange(len(labels))
    width = 0.3

    bars_min = plt.bar(x - width, mins, width, label='Min', color='skyblue')
    bars_mean = plt.bar(x, means, width, label='Mean', color='limegreen')
    bars_max = plt.bar(x + width, maxs, width, label='Max', color='orange')

    # Annotate the bars with values
    for bars, stat_values in zip([bars_min, bars_mean, bars_max], [mins, means, maxs]):
        for bar, value in zip(bars, stat_values):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f"{value:.2f}",
                     ha='center', va='bottom', fontsize=10)

    # Customization
    plt.xlabel("Operation")
    plt.ylabel("Time (ms)")
    plt.title("Rust Linked List | 10'000'000 elements")
    plt.xticks(x, labels, rotation=45)
    plt.legend()
    plt.tight_layout()

    # Save the plot
    plt.savefig("output_plot.png")
    print("Plot saved as 'output_plot_combined.png'")

# Example usage
if __name__ == "__main__":
    with open("log.txt", "r") as f:
        log_data = f.read()

    insert_front, insert_back, remove = process_log(log_data)
    plot_statistics(insert_front, insert_back, remove)
