#!/bin/bash
MODULE_NAME="C-List-Benchmark"
MODULE_FILE_NAME="list_benchmark"  # Name of your C kernel module
MODULE_SOURCE="list_benchmark.c"
MODULE_PATH="./"  # Path to the module's source directory
PERF_OUTPUT_DIR="./perf_output"  # Directory to store perf data

LOG_DIR="./logs"
LOG_FILE="$LOG_DIR/module_logs.txt"

PERF_EVENTS="cycles,instructions,cache-misses,page-faults,branch-misses,cpu-clock,branches"
SEED=12345  # Initial SEED value
I=1         # Initial I value
N_RUNS=2  # Number of iterations

# Ensure directories exist
mkdir -p "$LOG_DIR"
mkdir -p "$PERF_OUTPUT_DIR"

# Cleanup log file
> "$LOG_FILE"

# Function to wait for module initialization
wait_for_init() {
    echo "Waiting for module initialization...\n"
    while true; do
        if dmesg | tail -n 10 | grep -q "C-List-Benchmark: Module initialization complete"; then
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
    echo "Run $run with SEED=$SEED and I=$I\n"

    # Update SEED and I in the source code
    sed -i "s/#define SEED [0-9]*/#define SEED $SEED/" "$MODULE_PATH/$MODULE_SOURCE"
    sed -i "s/#define I [0-9]*/#define I $I/" "$MODULE_PATH/$MODULE_SOURCE"

    # Increment SEED and I
    ((SEED++))
    ((I++))

    # Rebuild the module
    make perf || { echo "Build failed!\n"; exit 1; }

    # Start perf recording
    PERF_OUTPUT="$PERF_OUTPUT_DIR/c-perf-list-$run.data"
    /usr/bin/perf record -e "$PERF_EVENTS" -g -a  --kernel-callchains -o "$PERF_OUTPUT" &

    PERF_PID=$!

    # Insert the module
    insmod "$MODULE_PATH/$MODULE_FILE_NAME.ko"

    # Wait for module initialization to complete
    wait_for_init

    # Capture kernel logs for this iteration
    echo "Logs for iteration $iter" >> "$LOG_FILE"
    dmesg | grep "$MODULE_NAME" >> "$LOG_FILE"

    # Remove the module unless it's the last iteration
    if [[ $run -lt N_RUNS ]]; then
        sudo rmmod "$MODULE_FILE_NAME"
    fi

    # Clear dmesg to avoid mixing logs between iterations
    dmesg -C

    # Stop perf recording
    kill -SIGINT "$PERF_PID"
    wait "$PERF_PID"
    
    echo "Finished test iteration $iter \n"
done

# Clean up build artifacts
echo "Cleaning up build artifacts...\n"
make  clean
echo "Build artifacts cleaned.\n"