import os
import csv
import re
import sys
from collections import defaultdict
import subprocess

# Constants
EVENT_CATEGORIES = [
    "cycles",
    "instructions",
    "cache-misses",
    "branch-misses",
    "cpu-clock",
    "branches"
]

FUNCTIONS = ["mutex_lock", "mutex_unlock"]
TMP_FILE = "tmp_report.txt"
OUTPUT_CSV = "./results/metrics.csv"

# Regex pattern to match only the target functions
METRIC_PATTERN = re.compile(rf"^\s*([\d.]+)%.*\[k\]\s+({'|'.join(FUNCTIONS)})")

# Parse the temporary txt file for metrics
def parse_tmp_file(tmp_file):
    metrics = defaultdict(lambda: defaultdict(list))
    current_event = None

    with open(tmp_file, "r") as file:
        for line in file:
            # Check if the line indicates a new event category
            for event in EVENT_CATEGORIES:
                if f"event '{event}'" in line:
                    current_event = event
                    break

            # Parse function metrics
            if current_event:
                match = METRIC_PATTERN.match(line)
                if match:
                    value, func_name = float(match.group(1)), match.group(2)
                    metrics[func_name][current_event].append(value)

    return metrics

# Append parsed metrics to the CSV file
def append_to_csv(metrics, output_csv):
    # Check if the file exists and load existing data
    existing_data = {}
    header_exists = os.path.isfile(output_csv) and os.path.getsize(output_csv) > 0

    if header_exists:
        with open(output_csv, "r") as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)  # Skip the header
            for row in reader:
                key = (row[0], row[1])  # (function, event)
                num_values = int(row[2])  # Number of captured values
                values = list(map(float, row[3:]))  # Extract values
                existing_data[key] = (num_values, values)

    # Update the data with the new metrics
    for func, events in metrics.items():
        for event, values in events.items():
            key = (func, event)
            if key in existing_data:
                current_num, current_values = existing_data[key]
                new_values = current_values + values
                existing_data[key] = (len(new_values), new_values)
            else:
                existing_data[key] = (len(values), values)

    # Write back the updated data to the CSV
    with open(output_csv, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow(["function", "event", "num_values", "values"])
        
        # Write rows
        for (func, event), (num_values, values) in existing_data.items():
            writer.writerow([func, event, num_values] + values)

# Main function to process a .data file
def process_perf_data(data_file, csv_file):
    # Convert .data file to temporary .txt file
    cmd = f"sudo perf report --stdio --kallsyms=/proc/kallsyms -i {data_file} -c insmod -n > {TMP_FILE}"
    print(f"Running command: {cmd}")  # Debug

    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error processing {data_file}: {e}")
        sys.exit(1)

    # Parse the temporary file and append metrics to CSV
    metrics = parse_tmp_file(TMP_FILE)
    append_to_csv(metrics, csv_file)

    # Clean up temporary file
    if os.path.exists(TMP_FILE):
        os.remove(TMP_FILE)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 extract_metrics.py <path_to_perf_data_file> <csv_file_name>")
        sys.exit(1)

    data_file = sys.argv[1]
    csv_file = sys.argv[2]
    if not os.path.exists(data_file):
        print(f"Error: {data_file} does not exist.")
        sys.exit(1)

    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} does not exist.")
        sys.exit(1)

    process_perf_data(data_file,csv_file)
