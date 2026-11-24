#!/bin/bash

set -e

echo "=== Running demo in Docker ==="

# Use a Ubuntu-based image with EDA tools pre-installed
docker run --rm -v $(pwd):/workdir -w /workdir ubuntu:22.04 bash -c "
apt-get update && apt-get install -y iverilog gtkwave xvfb &&
# Run the demo script with virtual X server for GTKWave
xvfb-run -a bash run_demo.sh
"

echo "Docker demo completed!"
