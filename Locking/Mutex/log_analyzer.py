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

    return total_times, min_time, max_time, avg_time

def plot_statistics(total_times, min_time, max_time, avg_time):
    # Create the plot
    plt.figure(figsize=(10, 6))
    entries = list(range(1, len(total_times) + 1))
    plt.plot(entries, total_times, marker="o", label="Total Lock/Unlock Time (ms)")

    # Add horizontal lines for min, max, and avg
    plt.axhline(y=min_time, color="g", linestyle="--", label=f"Min: {min_time} ms")
    plt.axhline(y=max_time, color="r", linestyle="--", label=f"Max: {max_time} ms")
    plt.axhline(y=avg_time, color="b", linestyle="--", label=f"Avg: {avg_time:.2f} ms")

    plt.xlabel("Test Number")
    plt.ylabel("Time (ms)")
    plt.title("C Mutex- lock/unlock 15000000 time")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Save the plot
    plt.savefig("mutex_benchmark_plot.png")
    print("Plot saved as 'mutex_benchmark_plot.png'.")

# Main function
if __name__ == "__main__":
    # Read the log file
    log_file_path = "log.txt"  # Replace with the actual path
    with open(log_file_path, "r") as file:
        log_data = file.read()

    # Process the log data
    total_times, min_time, max_time, avg_time = process_log(log_data)

    # Print statistics
    print(f"Total Lock/Unlock Time (ms): {total_times}")
    print(f"Min Time: {min_time} ms, Max Time: {max_time} ms, Avg Time: {avg_time:.2f} ms")

    # Generate the plot (saved only, not shown)
    plot_statistics(total_times, min_time, max_time, avg_time)

