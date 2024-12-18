import re
import numpy as np
import matplotlib.pyplot as plt

def process_log(log_data):
    # Regex pattern for extracting total lock/unlock times
    total_time_pattern = r"Total lock/unlock time: (\d+) ms"

    # Extract times using regex
    total_times = [int(m.group(1)) for m in re.finditer(total_time_pattern, log_data)]

    # Compute statistics
    min_time = np.min(total_times)
    max_time = np.max(total_times)
    avg_time = np.mean(total_times)
    var_time = np.var(total_times)
    median_time = np.median(total_times)

    return total_times, min_time, max_time, avg_time, var_time, median_time

def plot_statistics(total_times, min_time, max_time, avg_time, var_time, median_time):
    # Create the plot
    plt.figure(figsize=(10, 6))
    entries = list(range(1, len(total_times) + 1))
    plt.plot(entries, total_times, marker="o", label="Total Lock/Unlock Time (ms)")

    # Add horizontal lines for key statistics
    plt.axhline(y=min_time, color="g", linestyle="--", label=f"Min: {min_time} ms")
    plt.axhline(y=max_time, color="r", linestyle="--", label=f"Max: {max_time} ms")
    plt.axhline(y=avg_time, color="b", linestyle="--", label=f"Avg: {avg_time:.2f} ms")
    plt.axhline(y=median_time, color="orange", linestyle="--", label=f"Median: {median_time:.2f} ms")

    # Add variance to the legend
    variance_label = f"Variance: {var_time:.2f} ms²"
    plt.plot([], [], ' ', label=variance_label)  # Empty line for adding variance to legend

    plt.xlabel("Test Number")
    plt.ylabel("Time (ms)")
    plt.title("C Mutex - Lock/Unlock 15,000,000 Times")
    #plt.title("Rust Mutex - Lock/Unlock 15,000,000 Times")

    plt.legend(loc="upper right", fontsize=10, title="Legenda")
    plt.grid(True)
    plt.tight_layout()

    # Save the plot
    plt.savefig("mutex_benchmark_plot.png")
    print("Plot saved as 'mutex_benchmark_plot.png'.")

if __name__ == "__main__":
    # Read the log file
    log_file_path = "rust-log.txt"  # Replace with the actual path
    with open(log_file_path, "r") as file:
        log_data = file.read()

    # Process the log data
    total_times, min_time, max_time, avg_time, var_time, median_time = process_log(log_data)

    # Print statistics
    print("Statistics:")
    print(f"Total Lock/Unlock Times (ms): {total_times}")
    print(f"Min Time: {min_time} ms")
    print(f"Max Time: {max_time} ms")
    print(f"Avg Time: {avg_time:.2f} ms")
    print(f"Variance: {var_time:.2f} ms²")
    print(f"Median: {median_time:.2f} ms")

    # Generate the plot (saved only, not shown)
    plot_statistics(total_times, min_time, max_time, avg_time, var_time, median_time)
