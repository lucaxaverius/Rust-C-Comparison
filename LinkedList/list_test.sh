#!/bin/bash
# Run the C test script
cd ./C || exit
./run-test.sh

# Run the Rust test script
cd ../Rust || exit
./run-test.sh