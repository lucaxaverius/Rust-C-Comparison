import os
import re
import subprocess
import statistics
import sys
from collections import defaultdict

# Constants
EVENT_CATEGORIES = [
    "cycles",
    "instructions",
    "cache-misses",
    "branch-misses",
    "cpu-clock",
    "branches"
]
FUNCTIONS = ["insert_front", "insert_back", "iterate_all", "remove_all"]

PERF_DATA_DIR = "./perf_output"
TMP_FILE = "tmp_report.txt"
RESULTS_DIR = "./results"

# Regex to extract function metrics
METRIC_PATTERN = re.compile(r"^\s*([\d.]+)%.*\[k\]\s+(\w+)")

def run_perf_command(data_file, tmp_file):
    cmd = f"sudo perf report --stdio --kallsyms=/proc/kallsyms -i {data_file} -c insmod -n > {tmp_file}"
    # print(f"Running command: {cmd}")  # Debug
    try:
        subprocess.run(cmd, shell=True, check=True, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error while processing {data_file}: {e.stderr}")
        sys.exit(1)

def parse_tmp_file(tmp_file):
    metrics = defaultdict(lambda: defaultdict(list))
    current_event = None

    # print(f"Parsing file: {tmp_file}")  # Debug
    with open(tmp_file, "r") as file:
        for line in file:
            # Identify event categories
            for event in EVENT_CATEGORIES:
                if f"Samples: " in line and f"event '{event}'" in line:
                    current_event = event
                    # print(f"Found event category: {current_event}")  # Debug
                    break

            # Extract metrics for the specified functions
            if current_event:
                match = METRIC_PATTERN.match(line)
                if match:
                    value = float(match.group(1))
                    func_name = match.group(2)
                    # Only process functions we care about
                    if func_name in FUNCTIONS:
                        metrics[func_name][current_event].append(value)
                        #print(f"Captured metric: Function={func_name}, Event={current_event}, Value={value}")  # Debug
                    else:
                        print(f"Skipped function: {func_name}")  # Debug (for unexpected matches)

    # print(f"Parsed metrics: {metrics}")  # Debug
    return metrics


def calculate_statistics(data):
    if not data:
        print(f"No data to calculate statistics: {data}")  # Debug
        return {"avg": 0, "min": 0, "max": 0, "median": 0, "std_dev": 0}
    
    # print(f"Calculating statistics for data: {data}")  # Debug
    return {
        "avg": statistics.mean(data),
        "min": min(data),
        "max": max(data),
        "median": statistics.median(data),
        "std_dev": statistics.stdev(data) if len(data) > 1 else 0
    }

def process_perf_files(num_files):
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)

    aggregated_metrics = defaultdict(lambda: defaultdict(list))

    for i in range(1, num_files + 1):
        data_file = os.path.join(PERF_DATA_DIR, f"c-perf-list-{i}.data")
        print(f"Processing {data_file}...")  # Debug

        if not os.path.exists(data_file):
            print(f"File {data_file} does not exist. Skipping...")  # Debug
            continue

        # Convert .data to temporary .txt
        run_perf_command(data_file, TMP_FILE)

        # Parse the temporary file
        metrics = parse_tmp_file(TMP_FILE)

        # Aggregate metrics across files
        for func, events in metrics.items():
            for event, values in events.items():
                aggregated_metrics[func][event].extend(values)
        
        if os.path.exists(data_file)
            os.remove(data_file)

    # print(f"Aggregated metrics: {aggregated_metrics}")  # Debug

    # Remove the temporary file
    if os.path.exists(TMP_FILE):
        os.remove(TMP_FILE)

    # Calculate statistics across all files
    final_stats = {
        func: {event: calculate_statistics(values) for event, values in events.items()}
        for func, events in aggregated_metrics.items()
    }

    # print(f"Final statistics: {final_stats}")  # Debug
    return final_stats

def save_summary(summary):
    output_file = os.path.join(RESULTS_DIR, "summary.txt")
    with open(output_file, "w") as f:
        for func, events in summary.items():
            f.write(f"Function: {func}\n")
            for event, stats in events.items():
                f.write(f"  Event: {event}\n")
                f.write(f"    Avg: {stats['avg']:.2f}\n")
                f.write(f"    Min: {stats['min']:.2f}\n")
                f.write(f"    Max: {stats['max']:.2f}\n")
                f.write(f"    Median: {stats['median']:.2f}\n")
                f.write(f"    Std Dev: {stats['std_dev']:.2f}\n")
            f.write("\n")
    print(f"Summary saved to {output_file}")  # Debug

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 parse_perf.py <num_of_data_files>")
        sys.exit(1)

    num_files = int(sys.argv[1])
    summary = process_perf_files(num_files)
    save_summary(summary)
    print(f"Results saved in {RESULTS_DIR}/summary.txt")
