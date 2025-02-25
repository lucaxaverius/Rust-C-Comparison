#!/bin/bash
MODULE_NAME="Rust_SpinLock_Benchmark"
MODULE_FILE_NAME="rust_spinlock_benchmark"  # Name of your C kernel module
MODULE_SOURCE="rust_spinlock_benchmark.rs"
MODULE_PATH="./"  # Path to the module's source directory
PERF_OUTPUT_DIR="./perf_output"  # Directory to store perf data

LOG_DIR="./logs"
LOG_FILE="$LOG_DIR/module_logs.txt"

PERF_EVENTS="cycles,instructions,cache-misses,page-faults,branch-misses,cpu-clock,branches"
I=1         # Initial I value
N_RUNS=3  # Number of iterations 

SUMMARY_FILE="./results/summary.txt"
CSV_FILE="./results/metrics.csv"

# Ensure directories exist
mkdir -p "$LOG_DIR"
mkdir -p "$PERF_OUTPUT_DIR"

# Cleanup log file
> "$LOG_FILE"

# Clear previous results
> $CSV_FILE

# Function to wait for module initialization
wait_for_test() {
    echo "Waiting for module initialization...\n"
    while true; do
        if dmesg | tail -n 10 | grep -q "Rust_SpinLock_Benchmark: Test module completed"; then
            echo "Initialization detected!\n"
            break
        else
            sleep 1
        fi
    done
}

# Function to check if the module is loaded
is_module_loaded() {
    lsmod | grep -q "^$MODULE_FILE_NAME"
}

# Function to remove the module if loaded
remove_module_if_loaded() {
    if is_module_loaded; then
        echo "Module $MODULE_NAME is already loaded. Removing it..."
        sudo rmmod "$MODULE_FILE_NAME"
    fi
}

remove_module_if_loaded

for ((run=1; run<=N_RUNS; run++)); do
    echo "Run $run with I=$I\n"

    # Update ITERATION
    sed -i "s/^const ITERATION: i32 = [0-9]*/const ITERATION: i32 = $I/" "$MODULE_PATH/$MODULE_SOURCE"

    # Increment SEED and I
    ((I++))

    # Rebuild the module
    make || { echo "Build failed!\n"; exit 1; }

    # Start perf recording
    PERF_OUTPUT="$PERF_OUTPUT_DIR/rust-perf-spinlock-$run.data"
    /usr/bin/perf record -e "$PERF_EVENTS" -g -a --freq=1000 --kernel-callchains -o "$PERF_OUTPUT" &

    PERF_PID=$!

    # Insert the module
    insmod "$MODULE_PATH/$MODULE_FILE_NAME.ko"

    # Wait for module test completition
    wait_for_test

    # Stop perf recording
    kill -SIGINT "$PERF_PID"
    wait "$PERF_PID"

    # Save the metrics into the CSV file
    python3 extract_metrics.py "$PERF_OUTPUT" "$CSV_FILE"

    # Capture kernel logs for this iteration
    echo "Logs for iteration $run" >> "$LOG_FILE"
    dmesg | grep "$MODULE_NAME" >> "$LOG_FILE"

    # Remove the module unless it's the last iteration
    sudo rmmod "$MODULE_FILE_NAME"

    #rm "$PERF_OUTPUT"
    
    # Clear dmesg to avoid mixing logs between iterations
    dmesg -C
    
    echo "Finished test iteration $run \n"
done

python3 analyze_metrics.py "$CSV_FILE" "$SUMMARY_FILE"

# Clean up build artifacts
echo "Cleaning up build artifacts...\n"
make  clean
echo "Build artifacts cleaned.\n"